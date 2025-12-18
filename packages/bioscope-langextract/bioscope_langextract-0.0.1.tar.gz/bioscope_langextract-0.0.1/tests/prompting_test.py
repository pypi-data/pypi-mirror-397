# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import textwrap
import unittest

from langextract import prompting
from langextract.core import data
from langextract.core import format_handler as fh


class QAPromptGeneratorTest(unittest.TestCase):

  def test_generate_prompt(self):
    prompt_template_structured = prompting.PromptTemplateStructured(
        description=(
            "You are an assistant specialized in extracting key extractions"
            " from text.\nIdentify and extract important extractions such as"
            " people, places,\norganizations, dates, and medical conditions"
            " mentioned in the text.\n**Please ensure that the extractions"
            " are extracted in the same order as they\nappear in the source"
            " text.**\nProvide the extracted extractions in a structured"
            " YAML format."
        ),
        examples=[
            data.ExampleData(
                text=(
                    "The patient was diagnosed with hypertension and diabetes."
                ),
                extractions=[
                    data.Extraction(
                        extraction_text="hypertension",
                        extraction_class="medical_condition",
                        attributes={
                            "chronicity": "chronic",
                            "system": "cardiovascular",
                        },
                    ),
                    data.Extraction(
                        extraction_text="diabetes",
                        extraction_class="medical_condition",
                        attributes={
                            "chronicity": "chronic",
                            "system": "endocrine",
                        },
                    ),
                ],
            )
        ],
    )

    format_handler = fh.FormatHandler(
        format_type=data.FormatType.YAML,
        use_wrapper=True,
        wrapper_key="extractions",
        use_fences=True,
    )

    prompt_generator = prompting.QAPromptGenerator(
        template=prompt_template_structured,
        format_handler=format_handler,
        examples_heading="",
        question_prefix="",
        answer_prefix="",
    )

    actual_prompt_text = prompt_generator.render(
        "The patient reports chest pain and shortness of breath."
    )

    expected_prompt_text = textwrap.dedent(f"""\
            You are an assistant specialized in extracting key extractions from text.
            Identify and extract important extractions such as people, places,
            organizations, dates, and medical conditions mentioned in the text.
            **Please ensure that the extractions are extracted in the same order as they
            appear in the source text.**
            Provide the extracted extractions in a structured YAML format.


            The patient was diagnosed with hypertension and diabetes.
            ```yaml
            {data.EXTRACTIONS_KEY}:
            - medical_condition: hypertension
              medical_condition_attributes:
                chronicity: chronic
                system: cardiovascular
            - medical_condition: diabetes
              medical_condition_attributes:
                chronicity: chronic
                system: endocrine
            ```

            The patient reports chest pain and shortness of breath.
            """)
    self.assertEqual(expected_prompt_text, actual_prompt_text)

  def _test_format_example(
      self,
      format_type,
      example_text,
      example_extractions,
      expected_formatted_example,
      attribute_suffix="_attributes",
      require_extractions_key=True,
  ):
    """Tests formatting of examples in different formats and scenarios."""
    example_data = data.ExampleData(
        text=example_text,
        extractions=example_extractions,
    )

    structured_template = prompting.PromptTemplateStructured(
        description="Extract information from the text.",
        examples=[example_data],
    )

    format_handler = fh.FormatHandler(
        format_type=format_type,
        use_wrapper=require_extractions_key,
        wrapper_key="extractions" if require_extractions_key else None,
        use_fences=True,
        attribute_suffix=attribute_suffix,
    )

    prompt_generator = prompting.QAPromptGenerator(
        template=structured_template,
        format_handler=format_handler,
        question_prefix="",
        answer_prefix="",
    )

    actual_formatted_example = prompt_generator.format_example_as_text(
        example_data
    )
    self.assertEqual(expected_formatted_example, actual_formatted_example)

  def test_format_example_json_basic_format(self):
    """Test JSON basic format."""
    self._test_format_example(
        format_type=data.FormatType.JSON,
        example_text="Patient has diabetes and is prescribed insulin.",
        example_extractions=[
            data.Extraction(
                extraction_text="diabetes",
                extraction_class="medical_condition",
                attributes={"chronicity": "chronic"},
            ),
            data.Extraction(
                extraction_text="insulin",
                extraction_class="medication",
                attributes={"prescribed": "prescribed"},
            ),
        ],
        expected_formatted_example=textwrap.dedent(f"""\
                Patient has diabetes and is prescribed insulin.
                ```json
                {{
                  "{data.EXTRACTIONS_KEY}": [
                    {{
                      "medical_condition": "diabetes",
                      "medical_condition_attributes": {{
                        "chronicity": "chronic"
                      }}
                    }},
                    {{
                      "medication": "insulin",
                      "medication_attributes": {{
                        "prescribed": "prescribed"
                      }}
                    }}
                  ]
                }}
                ```
                """),
    )

  def test_format_example_yaml_basic_format(self):
    """Test YAML basic format."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text="Patient has diabetes and is prescribed insulin.",
        example_extractions=[
            data.Extraction(
                extraction_text="diabetes",
                extraction_class="medical_condition",
                attributes={"chronicity": "chronic"},
            ),
            data.Extraction(
                extraction_text="insulin",
                extraction_class="medication",
                attributes={"prescribed": "prescribed"},
            ),
        ],
        expected_formatted_example=textwrap.dedent(f"""\
                Patient has diabetes and is prescribed insulin.
                ```yaml
                {data.EXTRACTIONS_KEY}:
                - medical_condition: diabetes
                  medical_condition_attributes:
                    chronicity: chronic
                - medication: insulin
                  medication_attributes:
                    prescribed: prescribed
                ```
                """),
    )

  def test_format_example_custom_attribute_suffix(self):
    """Test custom attribute suffix."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text="Patient has a fever.",
        example_extractions=[
            data.Extraction(
                extraction_text="fever",
                extraction_class="symptom",
                attributes={"severity": "mild"},
            ),
        ],
        attribute_suffix="_props",
        expected_formatted_example=textwrap.dedent(f"""\
                Patient has a fever.
                ```yaml
                {data.EXTRACTIONS_KEY}:
                - symptom: fever
                  symptom_props:
                    severity: mild
                ```
                """),
    )

  def test_format_example_yaml_empty_extractions(self):
    """Test YAML with empty extractions."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text="Text with no extractions.",
        example_extractions=[],
        expected_formatted_example=textwrap.dedent(f"""\
                Text with no extractions.
                ```yaml
                {data.EXTRACTIONS_KEY}: []
                ```
                """),
    )

  def test_format_example_json_empty_extractions(self):
    """Test JSON with empty extractions."""
    self._test_format_example(
        format_type=data.FormatType.JSON,
        example_text="Text with no extractions.",
        example_extractions=[],
        expected_formatted_example=textwrap.dedent(f"""\
                Text with no extractions.
                ```json
                {{
                  "{data.EXTRACTIONS_KEY}": []
                }}
                ```
                """),
    )

  def test_format_example_yaml_empty_attributes(self):
    """Test YAML with empty attributes."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text="Patient is resting comfortably.",
        example_extractions=[
            data.Extraction(
                extraction_text="Patient",
                extraction_class="person",
                attributes={},
            ),
        ],
        expected_formatted_example=textwrap.dedent(f"""\
                Patient is resting comfortably.
                ```yaml
                {data.EXTRACTIONS_KEY}:
                - person: Patient
                  person_attributes: {{}}
                ```
                """),
    )

  def test_format_example_json_empty_attributes(self):
    """Test JSON with empty attributes."""
    self._test_format_example(
        format_type=data.FormatType.JSON,
        example_text="Patient is resting comfortably.",
        example_extractions=[
            data.Extraction(
                extraction_text="Patient",
                extraction_class="person",
                attributes={},
            ),
        ],
        expected_formatted_example=textwrap.dedent(f"""\
                Patient is resting comfortably.
                ```json
                {{
                  "{data.EXTRACTIONS_KEY}": [
                    {{
                      "person": "Patient",
                      "person_attributes": {{}}
                    }}
                  ]
                }}
                ```
                """),
    )

  def test_format_example_yaml_same_extraction_class_multiple_times(self):
    """Test YAML with same extraction class multiple times."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text=(
            "Patient has multiple medications: aspirin and lisinopril."
        ),
        example_extractions=[
            data.Extraction(
                extraction_text="aspirin",
                extraction_class="medication",
                attributes={"dosage": "81mg"},
            ),
            data.Extraction(
                extraction_text="lisinopril",
                extraction_class="medication",
                attributes={"dosage": "10mg"},
            ),
        ],
        expected_formatted_example=textwrap.dedent(f"""\
                Patient has multiple medications: aspirin and lisinopril.
                ```yaml
                {data.EXTRACTIONS_KEY}:
                - medication: aspirin
                  medication_attributes:
                    dosage: 81mg
                - medication: lisinopril
                  medication_attributes:
                    dosage: 10mg
                ```
                """),
    )

  def test_format_example_json_simplified_no_extractions_key(self):
    """Test JSON without extractions key."""
    self._test_format_example(
        format_type=data.FormatType.JSON,
        example_text="Patient has diabetes and is prescribed insulin.",
        example_extractions=[
            data.Extraction(
                extraction_text="diabetes",
                extraction_class="medical_condition",
                attributes={"chronicity": "chronic"},
            ),
            data.Extraction(
                extraction_text="insulin",
                extraction_class="medication",
                attributes={"prescribed": "prescribed"},
            ),
        ],
        require_extractions_key=False,
        expected_formatted_example=textwrap.dedent("""\
                Patient has diabetes and is prescribed insulin.
                ```json
                [
                  {
                    "medical_condition": "diabetes",
                    "medical_condition_attributes": {
                      "chronicity": "chronic"
                    }
                  },
                  {
                    "medication": "insulin",
                    "medication_attributes": {
                      "prescribed": "prescribed"
                    }
                  }
                ]
                ```
                """),
    )

  def test_format_example_yaml_simplified_no_extractions_key(self):
    """Test YAML without extractions key."""
    self._test_format_example(
        format_type=data.FormatType.YAML,
        example_text="Patient has a fever.",
        example_extractions=[
            data.Extraction(
                extraction_text="fever",
                extraction_class="symptom",
                attributes={"severity": "mild"},
            ),
        ],
        require_extractions_key=False,
        expected_formatted_example=textwrap.dedent("""\
                Patient has a fever.
                ```yaml
                - symptom: fever
                  symptom_attributes:
                    severity: mild
                ```
                """),
    )


if __name__ == "__main__":
  unittest.main()
