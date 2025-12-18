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
from typing import Sequence
import unittest

from langextract import chunking
from langextract import resolver as resolver_lib
from langextract.core import data
from langextract.core import tokenizer


def assert_char_interval_match_source(
    test_case: unittest.TestCase,
    source_text: str,
    extractions: Sequence[data.Extraction],
):
  """Asserts that the char_interval of matched extractions matches the source text."""
  for extraction in extractions:
    if extraction.alignment_status == data.AlignmentStatus.MATCH_EXACT:
      assert (
          extraction.char_interval is not None
      ), "char_interval should not be None for AlignmentStatus.MATCH_EXACT"

      char_int = extraction.char_interval
      start = char_int.start_pos
      end = char_int.end_pos
      test_case.assertIsNotNone(start, "start_pos should not be None")
      test_case.assertIsNotNone(end, "end_pos should not be None")
      extracted = source_text[start:end]
      test_case.assertEqual(
          extracted.lower(),
          extraction.extraction_text.lower(),
          f"Extraction '{extraction.extraction_text}' does not match extracted"
          f" '{extracted}' using char_interval {char_int}",
      )


class ParserTest(unittest.TestCase):

  def _test_parser_error_case(
      self, resolver, input_text, expected_exception, expected_regex
  ):
    with self.assertRaisesRegex(expected_exception, expected_regex):
      resolver.string_to_extraction_data(input_text)

  def test_parser_error_json_invalid_input(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.JSON,
            fence_output=True,
            strict_fences=True,
        ),
        input_text="invalid input",
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=".*fence markers.*",
    )

  def test_parser_error_json_missing_markers(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.JSON,
            fence_output=True,
            strict_fences=True,
        ),
        input_text='[{"key": "value"}]',
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=".*fence markers.*",
    )

  def test_parser_error_json_empty_string(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.JSON,
            fence_output=True,
        ),
        input_text="",
        expected_exception=ValueError,
        expected_regex=".*must be a non-empty string.*",
    )

  def test_parser_error_json_partial_markers(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.JSON,
            fence_output=True,
            strict_fences=True,
        ),
        input_text='```json\n{"key": "value"',
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=".*fence markers.*",
    )

  def test_parser_error_yaml_invalid_input(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.YAML,
            fence_output=True,
            strict_fences=True,
        ),
        input_text="invalid input",
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=".*fence markers.*",
    )

  def test_parser_error_yaml_missing_markers(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.YAML,
            fence_output=True,
            strict_fences=True,
        ),
        input_text='[{"key": "value"}]',
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=".*fence markers.*",
    )

  def test_parser_error_yaml_empty_content(self):
    self._test_parser_error_case(
        resolver=resolver_lib.Resolver(
            format_type=data.FormatType.YAML,
            fence_output=True,
        ),
        input_text="```yaml\n```",
        expected_exception=resolver_lib.ResolverParsingError,
        expected_regex=(
            f".*Content must be a mapping with an '{data.EXTRACTIONS_KEY}'"
            " key.*"
        ),
    )


class ExtractOrderedEntitiesTest(unittest.TestCase):

  def _test_extract_ordered_extractions_success(
      self,
      test_input,
      expected_output,
      resolver=None,
  ):
    if resolver is None:
      resolver = resolver_lib.Resolver(
          extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX
      )
    actual_output = resolver.extract_ordered_extractions(test_input)
    self.assertEqual(actual_output, expected_output)

  def test_valid_input(self):
    self._test_extract_ordered_extractions_success(
        test_input=[
            {
                "medication": "Naprosyn",
                "medication_index": 4,
                "frequency": "as needed",
                "frequency_index": 5,
                "reason": "pain",
                "reason_index": 8,
            },
            {
                "medication": "prednisone",
                "medication_index": 5,
                "frequency": "daily",
                "frequency_index": 1,
            },
        ],
        expected_output=[
            data.Extraction(
                extraction_class="frequency",
                extraction_text="daily",
                extraction_index=1,
                group_index=1,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Naprosyn",
                extraction_index=4,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="frequency",
                extraction_text="as needed",
                extraction_index=5,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="prednisone",
                extraction_index=5,
                group_index=1,
            ),
            data.Extraction(
                extraction_class="reason",
                extraction_text="pain",
                extraction_index=8,
                group_index=0,
            ),
        ],
    )

  def test_empty_input(self):
    self._test_extract_ordered_extractions_success(
        test_input=[],
        expected_output=[],
    )

  def test_mixed_index_order(self):
    self._test_extract_ordered_extractions_success(
        test_input=[
            {
                "medication": "Ibuprofen",
                "medication_index": 2,
                "dosage": "400mg",
                "dosage_index": 1,
            },
            {
                "medication": "Acetaminophen",
                "medication_index": 1,
                "duration": "7 days",
                "duration_index": 2,
            },
        ],
        expected_output=[
            data.Extraction(
                extraction_class="dosage",
                extraction_text="400mg",
                extraction_index=1,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Acetaminophen",
                extraction_index=1,
                group_index=1,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Ibuprofen",
                extraction_index=2,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="duration",
                extraction_text="7 days",
                extraction_index=2,
                group_index=1,
            ),
        ],
    )

  def test_missing_index_key(self):
    self._test_extract_ordered_extractions_success(
        test_input=[{
            "medication": "Aspirin",
            "dosage": "325mg",
            "dosage_index": 1,
        }],
        expected_output=[
            data.Extraction(
                extraction_class="dosage",
                extraction_text="325mg",
                extraction_index=1,
                group_index=0,
            ),
        ],
    )

  def test_all_indices_missing(self):
    self._test_extract_ordered_extractions_success(
        test_input=[
            {"medication": "Aspirin", "dosage": "325mg"},
            {"medication": "Ibuprofen", "dosage": "400mg"},
        ],
        expected_output=[],
    )

  def test_single_element_dictionaries(self):
    self._test_extract_ordered_extractions_success(
        test_input=[
            {"medication": "Aspirin", "medication_index": 1},
            {"medication": "Ibuprofen", "medication_index": 2},
        ],
        expected_output=[
            data.Extraction(
                extraction_class="medication",
                extraction_text="Aspirin",
                extraction_index=1,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Ibuprofen",
                extraction_index=2,
                group_index=1,
            ),
        ],
    )

  def test_duplicate_indices_unchanged(self):
    self._test_extract_ordered_extractions_success(
        test_input=[{
            "medication": "Aspirin",
            "medication_index": 1,
            "dosage": "325mg",
            "dosage_index": 1,
            "form": "tablet",
            "form_index": 1,
        }],
        expected_output=[
            data.Extraction(
                extraction_class="medication",
                extraction_text="Aspirin",
                extraction_index=1,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="dosage",
                extraction_text="325mg",
                extraction_index=1,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="form",
                extraction_text="tablet",
                extraction_index=1,
                group_index=0,
            ),
        ],
    )

  def test_negative_indices(self):
    self._test_extract_ordered_extractions_success(
        test_input=[{
            "medication": "Aspirin",
            "medication_index": -1,
            "dosage": "325mg",
            "dosage_index": -2,
        }],
        expected_output=[
            data.Extraction(
                extraction_class="dosage",
                extraction_text="325mg",
                extraction_index=-2,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Aspirin",
                extraction_index=-1,
                group_index=0,
            ),
        ],
    )

  def test_index_without_data_key_ignored(self):
    self._test_extract_ordered_extractions_success(
        test_input=[{
            "medication_index": 1,
            "dosage": "325mg",
            "dosage_index": 2,
        }],
        expected_output=[
            data.Extraction(
                extraction_class="dosage",
                extraction_text="325mg",
                extraction_index=2,
                group_index=0,
            ),
        ],
    )

  def test_no_index_suffix(self):
    self._test_extract_ordered_extractions_success(
        resolver=resolver_lib.Resolver(
            extraction_index_suffix=None,
            format_type=data.FormatType.JSON,
        ),
        test_input=[
            {"medication": "Aspirin"},
            {"medication": "Ibuprofen"},
            {"dosage": "325mg"},
            {"dosage": "400mg"},
        ],
        expected_output=[
            data.Extraction(
                extraction_class="medication",
                extraction_text="Aspirin",
                extraction_index=1,
                group_index=0,
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Ibuprofen",
                extraction_index=2,
                group_index=1,
            ),
            data.Extraction(
                extraction_class="dosage",
                extraction_text="325mg",
                extraction_index=3,
                group_index=2,
            ),
            data.Extraction(
                extraction_class="dosage",
                extraction_text="400mg",
                extraction_index=4,
                group_index=3,
            ),
        ],
    )

  def test_attributes_suffix(self):
    self._test_extract_ordered_extractions_success(
        resolver=resolver_lib.Resolver(
            extraction_index_suffix=None,
            format_type=data.FormatType.JSON,
        ),
        test_input=[
            {
                "patient": "Jane Doe",
                "patient_attributes": {
                    "PERSON": "True",
                    "IDENTIFIABLE": "True",
                },
            },
            {
                "medication": "Lisinopril",
                "medication_attributes": {
                    "THERAPEUTIC": "True",
                    "CLINICAL": "True",
                },
            },
        ],
        expected_output=[
            data.Extraction(
                extraction_class="patient",
                extraction_text="Jane Doe",
                extraction_index=1,
                group_index=0,
                attributes={
                    "PERSON": "True",
                    "IDENTIFIABLE": "True",
                },
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Lisinopril",
                extraction_index=2,
                group_index=1,
                attributes={
                    "THERAPEUTIC": "True",
                    "CLINICAL": "True",
                },
            ),
        ],
    )

  def test_indices_and_attributes(self):
    self._test_extract_ordered_extractions_success(
        test_input=[
            {
                "patient": "John Doe",
                "patient_index": 2,
                "patient_attributes": {
                    "IDENTIFIABLE": "True",
                },
                "condition": "hypertension",
                "condition_index": 1,
                "condition_attributes": {
                    "CHRONIC_CONDITION": "True",
                    "REQUIRES_MANAGEMENT": "True",
                },
            },
            {
                "medication": "Lisinopril",
                "medication_index": 3,
                "medication_attributes": {
                    "ANTIHYPERTENSIVE_MEDICATION": "True",
                    "DAILY_USE": "True",
                },
                "dosage": "10mg",
                "dosage_index": 4,
                "dosage_attributes": {
                    "STANDARD_DAILY_DOSE": "True",
                },
            },
        ],
        expected_output=[
            data.Extraction(
                extraction_class="condition",
                extraction_text="hypertension",
                extraction_index=1,
                group_index=0,
                attributes={
                    "CHRONIC_CONDITION": "True",
                    "REQUIRES_MANAGEMENT": "True",
                },
            ),
            data.Extraction(
                extraction_class="patient",
                extraction_text="John Doe",
                extraction_index=2,
                group_index=0,
                attributes={
                    "IDENTIFIABLE": "True",
                },
            ),
            data.Extraction(
                extraction_class="medication",
                extraction_text="Lisinopril",
                extraction_index=3,
                group_index=1,
                attributes={
                    "ANTIHYPERTENSIVE_MEDICATION": "True",
                    "DAILY_USE": "True",
                },
            ),
            data.Extraction(
                extraction_class="dosage",
                extraction_text="10mg",
                extraction_index=4,
                group_index=1,
                attributes={
                    "STANDARD_DAILY_DOSE": "True",
                },
            ),
        ],
    )

  def test_non_integer_indices_raises(self):
    resolver = resolver_lib.Resolver(
        format_type=data.FormatType.JSON,
        extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
    )
    test_input = [{
        "medication": "Aspirin",
        "medication_index": "first",
        "dosage": "325mg",
        "dosage_index": "second",
    }]
    with self.assertRaisesRegex(ValueError, ".*must be an integer.*"):
      resolver.extract_ordered_extractions(test_input)

  def test_float_indices_raises(self):
    resolver = resolver_lib.Resolver(
        format_type=data.FormatType.JSON,
        extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
    )
    test_input = [{"medication": "Aspirin", "medication_index": 1.0}]
    with self.assertRaisesRegex(ValueError, ".*must be an integer.*"):
      resolver.extract_ordered_extractions(test_input)


class AlignEntitiesTest(unittest.TestCase):
  _SOURCE_TEXT_TWO_MEDS = (
      "Patient is prescribed Naprosyn and prednisone for treatment."
  )
  _SOURCE_TEXT_THREE_CONDITIONS_AND_MEDS = (
      "Patient with arthritis, fever, and inflammation is prescribed"
      " Naprosyn, prednisone, and ibuprofen."
  )
  _SOURCE_TEXT_MULTI_WORD_EXTRACTIONS = (
      "Pt was prescribed Naprosyn as needed for pain and prednisone for"
      " one month."
  )

  def setUp(self):
    super().setUp()
    self.aligner = resolver_lib.WordAligner()
    self.maxDiff = 10000

  def _test_extraction_alignment(
      self,
      extractions: Sequence[Sequence[data.Extraction]],
      source_text: str,
      expected_output: Sequence[Sequence[data.Extraction]] | type,
      enable_fuzzy_alignment: bool = False,
      accept_match_lesser: bool = True,
  ):
    if expected_output is ValueError:
      with self.assertRaises(ValueError):
        self.aligner.align_extractions(
            extractions, source_text, enable_fuzzy_alignment=False
        )
    else:
      aligned_extraction_groups = self.aligner.align_extractions(
          extractions,
          source_text,
          enable_fuzzy_alignment=enable_fuzzy_alignment,
          accept_match_lesser=accept_match_lesser,
      )
      flattened_extractions = []
      for group in aligned_extraction_groups:
        flattened_extractions.extend(group)
      assert_char_interval_match_source(
          self, source_text, flattened_extractions
      )
      self.assertEqual(aligned_extraction_groups, expected_output)

  def test_basic_alignment(self):
    self._test_extraction_alignment(
        extractions=[
            [
                data.Extraction(
                    extraction_class="medication", extraction_text="Naprosyn"
                )
            ],
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="prednisone",
                )
            ],
        ],
        source_text=self._SOURCE_TEXT_TWO_MEDS,
        expected_output=[
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="Naprosyn",
                    token_interval=tokenizer.TokenInterval(
                        start_index=3, end_index=4
                    ),
                    char_interval=data.CharInterval(start_pos=22, end_pos=30),
                    alignment_status=data.AlignmentStatus.MATCH_EXACT,
                )
            ],
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="prednisone",
                    token_interval=tokenizer.TokenInterval(
                        start_index=5, end_index=6
                    ),
                    char_interval=data.CharInterval(start_pos=35, end_pos=45),
                    alignment_status=data.AlignmentStatus.MATCH_EXACT,
                )
            ],
        ],
    )

  def test_extraction_not_found(self):
    self._test_extraction_alignment(
        extractions=[[
            data.Extraction(
                extraction_class="medication", extraction_text="aspirin"
            )
        ]],
        source_text=self._SOURCE_TEXT_TWO_MEDS,
        expected_output=[[
            data.Extraction(
                extraction_class="medication",
                extraction_text="aspirin",
                char_interval=None,
            )
        ]],
    )

  def test_empty_source_text_raises(self):
    self._test_extraction_alignment(
        extractions=[[
            data.Extraction(
                extraction_class="medication", extraction_text="Naprosyn"
            )
        ]],
        source_text="",
        expected_output=ValueError,
    )

  def test_empty_extractions_list(self):
    self._test_extraction_alignment(
        extractions=[],
        source_text=self._SOURCE_TEXT_TWO_MEDS,
        expected_output=[],
    )

  def test_case_insensitivity(self):
    self._test_extraction_alignment(
        extractions=[
            [
                data.Extraction(
                    extraction_class="medication", extraction_text="naprosyn"
                )
            ],
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="PREDNISONE",
                )
            ],
        ],
        source_text=self._SOURCE_TEXT_TWO_MEDS.lower(),
        expected_output=[
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="naprosyn",
                    token_interval=tokenizer.TokenInterval(
                        start_index=3, end_index=4
                    ),
                    char_interval=data.CharInterval(start_pos=22, end_pos=30),
                    alignment_status=data.AlignmentStatus.MATCH_EXACT,
                )
            ],
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="PREDNISONE",
                    token_interval=tokenizer.TokenInterval(
                        start_index=5, end_index=6
                    ),
                    char_interval=data.CharInterval(start_pos=35, end_pos=45),
                    alignment_status=data.AlignmentStatus.MATCH_EXACT,
                )
            ],
        ],
    )

  def test_fuzzy_alignment_success(self):
    self._test_extraction_alignment(
        extractions=[
            [
                data.Extraction(
                    extraction_class="condition",
                    extraction_text="heart problems",
                )
            ],
            [
                data.Extraction(
                    extraction_class="condition",
                    extraction_text="severe heart problems complications",
                )
            ],
        ],
        source_text="Patient has severe heart problems today.",
        expected_output=[
            [
                data.Extraction(
                    extraction_class="condition",
                    extraction_text="heart problems",
                    token_interval=tokenizer.TokenInterval(
                        start_index=3, end_index=5
                    ),
                    char_interval=data.CharInterval(start_pos=19, end_pos=33),
                    alignment_status=data.AlignmentStatus.MATCH_FUZZY,
                )
            ],
            [
                data.Extraction(
                    extraction_class="condition",
                    extraction_text="severe heart problems complications",
                    token_interval=tokenizer.TokenInterval(
                        start_index=2, end_index=5
                    ),
                    char_interval=data.CharInterval(start_pos=12, end_pos=33),
                    alignment_status=data.AlignmentStatus.MATCH_LESSER,
                )
            ],
        ],
        enable_fuzzy_alignment=True,
    )

  def test_fuzzy_alignment_below_threshold(self):
    self._test_extraction_alignment(
        extractions=[
            [
                data.Extraction(
                    extraction_class="medication",
                    extraction_text="completely different medicine",
                )
            ],
        ],
        source_text="Patient takes aspirin daily.",
        expected_output=[[
            data.Extraction(
                extraction_class="medication",
                extraction_text="completely different medicine",
                char_interval=None,
                alignment_status=None,
            )
        ]],
        enable_fuzzy_alignment=True,
    )


class ResolverTest(unittest.TestCase):
  _TWO_MEDICATIONS_JSON_UNDELIMITED = textwrap.dedent(f"""\
        {{
          "{data.EXTRACTIONS_KEY}": [
            {{
              "medication": "Naprosyn",
              "medication_index": 4,
              "frequency": "as needed",
              "frequency_index": 5,
              "reason": "pain",
              "reason_index": 8
            }},
            {{
              "medication": "prednisone",
              "medication_index": 9,
              "duration": "for one month",
              "duration_index": 10
            }}
          ]
        }}""")

  _TWO_MEDICATIONS_YAML_UNDELIMITED = textwrap.dedent(f"""\
    {data.EXTRACTIONS_KEY}:
      - medication: "Naprosyn"
        medication_index: 4
        frequency: "as needed"
        frequency_index: 5
        reason: "pain"
        reason_index: 8

      - medication: "prednisone"
        medication_index: 9
        duration: "for one month"
        duration_index: 10
    """)

  _EXPECTED_TWO_MEDICATIONS_ANNOTATED = [
      data.Extraction(
          extraction_class="medication",
          extraction_text="Naprosyn",
          extraction_index=4,
          group_index=0,
      ),
      data.Extraction(
          extraction_class="frequency",
          extraction_text="as needed",
          extraction_index=5,
          group_index=0,
      ),
      data.Extraction(
          extraction_class="reason",
          extraction_text="pain",
          extraction_index=8,
          group_index=0,
      ),
      data.Extraction(
          extraction_class="medication",
          extraction_text="prednisone",
          extraction_index=9,
          group_index=1,
      ),
      data.Extraction(
          extraction_class="duration",
          extraction_text="for one month",
          extraction_index=10,
          group_index=1,
      ),
  ]

  def setUp(self):
    super().setUp()
    self.default_resolver = resolver_lib.Resolver(
        format_type=data.FormatType.JSON,
        extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
    )

  def _test_resolve_valid_inputs(self, resolver, input_text, expected_output):
    actual_extractions = resolver.resolve(input_text)
    self.assertCountEqual(expected_output, actual_extractions)
    assert_char_interval_match_source(self, input_text, actual_extractions)

  def test_resolve_json_with_fence(self):
    self._test_resolve_valid_inputs(
        resolver=resolver_lib.Resolver(
            fence_output=True,
            format_type=data.FormatType.JSON,
            extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
        ),
        input_text=textwrap.dedent(f"""\
                ```json
                {{
                  "{data.EXTRACTIONS_KEY}": [
                    {{
                      "medication": "Naprosyn",
                      "medication_index": 4,
                      "frequency": "as needed",
                      "frequency_index": 5,
                      "reason": "pain",
                      "reason_index": 8
                    }},
                    {{
                      "medication": "prednisone",
                      "medication_index": 9,
                      "duration": "for one month",
                      "duration_index": 10
                    }}
                  ]
                }}
                ```"""),
        expected_output=self._EXPECTED_TWO_MEDICATIONS_ANNOTATED,
    )

  def test_resolve_yaml_with_fence(self):
    self._test_resolve_valid_inputs(
        resolver=resolver_lib.Resolver(
            fence_output=True,
            format_type=data.FormatType.YAML,
            extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
        ),
        input_text=textwrap.dedent(f"""\
                ```yaml
                {data.EXTRACTIONS_KEY}:
                  - medication: "Naprosyn"
                    medication_index: 4
                    frequency: "as needed"
                    frequency_index: 5
                    reason: "pain"
                    reason_index: 8

                  - medication: "prednisone"
                    medication_index: 9
                    duration: "for one month"
                    duration_index: 10
                ```"""),
        expected_output=self._EXPECTED_TWO_MEDICATIONS_ANNOTATED,
    )

  def test_resolve_json_no_fence(self):
    self._test_resolve_valid_inputs(
        resolver=resolver_lib.Resolver(
            fence_output=False,
            format_type=data.FormatType.JSON,
            extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
        ),
        input_text=self._TWO_MEDICATIONS_JSON_UNDELIMITED,
        expected_output=self._EXPECTED_TWO_MEDICATIONS_ANNOTATED,
    )

  def test_resolve_yaml_no_fence(self):
    self._test_resolve_valid_inputs(
        resolver=resolver_lib.Resolver(
            fence_output=False,
            format_type=data.FormatType.YAML,
            extraction_index_suffix=resolver_lib.DEFAULT_INDEX_SUFFIX,
        ),
        input_text=self._TWO_MEDICATIONS_YAML_UNDELIMITED,
        expected_output=self._EXPECTED_TWO_MEDICATIONS_ANNOTATED,
    )

  def test_handle_integer_extraction(self):
    test_input = textwrap.dedent(f"""\
        ```json
        {{
          "{data.EXTRACTIONS_KEY}": [
            {{
              "year": 2006,
              "year_index": 6
            }}
          ]
        }}
        ```""")
    expected_extractions = [
        data.Extraction(
            extraction_class="year",
            extraction_text="2006",
            extraction_index=6,
            group_index=0,
        )
    ]

    actual_extractions = self.default_resolver.resolve(test_input)
    self.assertEqual(expected_extractions, list(actual_extractions))

  def test_resolve_empty_yaml(self):
    test_input = "```json\n```"
    actual = self.default_resolver.resolve(
        test_input, suppress_parse_errors=True
    )
    self.assertEqual(len(actual), 0)

  def test_resolve_empty_yaml_without_suppress_parse_errors(self):
    test_input = "```json\n```"
    with self.assertRaises(resolver_lib.ResolverParsingError):
      self.default_resolver.resolve(test_input, suppress_parse_errors=False)

  def test_align_with_valid_chunk(self):
    text = "This is a sample text with some extractions."
    tokenized_text = tokenizer.tokenize(text)

    chunk = tokenizer.TokenInterval(start_index=0, end_index=8)
    annotated_extractions = [
        data.Extraction(
            extraction_class="medication", extraction_text="sample"
        ),
        data.Extraction(
            extraction_class="condition", extraction_text="extractions"
        ),
    ]
    expected_extractions = [
        data.Extraction(
            extraction_class="medication",
            extraction_text="sample",
            token_interval=tokenizer.TokenInterval(start_index=3, end_index=4),
            char_interval=data.CharInterval(start_pos=10, end_pos=16),
            alignment_status=data.AlignmentStatus.MATCH_EXACT,
        ),
        data.Extraction(
            extraction_class="condition",
            extraction_text="extractions",
            token_interval=tokenizer.TokenInterval(start_index=7, end_index=8),
            char_interval=data.CharInterval(start_pos=32, end_pos=43),
            alignment_status=data.AlignmentStatus.MATCH_EXACT,
        ),
    ]

    chunk_text = chunking.get_token_interval_text(tokenized_text, chunk)
    token_offset = chunk.start_index
    aligned_extractions = list(
        self.default_resolver.align(
            extractions=annotated_extractions,
            source_text=chunk_text,
            token_offset=token_offset,
            char_offset=0,
            enable_fuzzy_alignment=False,
        )
    )

    self.assertEqual(len(aligned_extractions), len(expected_extractions))
    for expected, actual in zip(expected_extractions, aligned_extractions):
      self.assertEqual(expected, actual)
    assert_char_interval_match_source(self, text, aligned_extractions)

  def test_align_with_no_extractions_in_chunk(self):
    tokenized_text = tokenizer.tokenize("No extractions here.")

    chunk = tokenizer.TokenInterval()
    chunk.start_index = 0
    chunk.end_index = 3
    annotated_extractions = []

    chunk_text = chunking.get_token_interval_text(tokenized_text, chunk)
    token_offset = chunk.start_index
    aligned_extractions = list(
        self.default_resolver.align(
            extractions=annotated_extractions,
            source_text=chunk_text,
            token_offset=token_offset,
            char_offset=0,
            enable_fuzzy_alignment=False,
        )
    )

    self.assertEqual(len(aligned_extractions), 0)

  def test_align_successful(self):
    tokenized_text = tokenizer.TokenizedText(
        text="zero one two",
        tokens=[
            tokenizer.Token(
                token_type=tokenizer.TokenType.WORD,
                char_interval=tokenizer.CharInterval(start_pos=0, end_pos=4),
                index=0,
            ),
            tokenizer.Token(
                token_type=tokenizer.TokenType.WORD,
                char_interval=tokenizer.CharInterval(start_pos=5, end_pos=8),
                index=1,
            ),
            tokenizer.Token(
                token_type=tokenizer.TokenType.WORD,
                char_interval=tokenizer.CharInterval(start_pos=9, end_pos=12),
                index=2,
            ),
        ],
    )

    chunk = tokenizer.TokenInterval(start_index=0, end_index=3)
    annotated_extractions = [
        data.Extraction(extraction_class="foo", extraction_text="zero"),
        data.Extraction(extraction_class="foo", extraction_text="one"),
    ]

    chunk_text = chunking.get_token_interval_text(tokenized_text, chunk)
    token_offset = chunk.start_index
    aligned_extractions = list(
        self.default_resolver.align(
            extractions=annotated_extractions,
            source_text=chunk_text,
            token_offset=token_offset,
            char_offset=0,
            enable_fuzzy_alignment=False,
        )
    )

    self.assertEqual(len(aligned_extractions), 2)
    assert_char_interval_match_source(
        self, tokenized_text.text, aligned_extractions
    )

  def test_align_with_empty_annotated_extractions(self):
    """Test align method with empty annotated_extractions sequence."""
    tokenized_text = tokenizer.tokenize("No extractions here.")

    chunk = tokenizer.TokenInterval()
    chunk.start_index = 0
    chunk.end_index = 3
    annotated_extractions = []

    chunk_text = chunking.get_token_interval_text(tokenized_text, chunk)
    token_offset = chunk.start_index
    aligned_extractions = list(
        self.default_resolver.align(
            extractions=annotated_extractions,
            source_text=chunk_text,
            token_offset=token_offset,
            char_offset=0,
            enable_fuzzy_alignment=False,
        )
    )

    self.assertEqual(len(aligned_extractions), 0)


class FenceFallbackTest(unittest.TestCase):
  """Tests for fence marker fallback behavior."""

  def _test_parsing_scenario(
      self,
      test_input,
      fence_output,
      strict_fences,
      expected_key,
      expected_value,
  ):
    resolver = resolver_lib.Resolver(
        fence_output=fence_output,
        format_type=data.FormatType.JSON,
        strict_fences=strict_fences,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 1)
    self.assertIn(expected_key, result[0])
    self.assertEqual(result[0][expected_key], expected_value)

  def test_with_valid_fences(self):
    self._test_parsing_scenario(
        test_input=textwrap.dedent("""\
                ```json
                {
                  "extractions": [
                    {"person": "Marie Curie", "person_attributes": {"field": "physics"}}
                  ]
                }
                ```"""),
        fence_output=True,
        strict_fences=False,
        expected_key="person",
        expected_value="Marie Curie",
    )

  def test_fallback_no_fences(self):
    self._test_parsing_scenario(
        test_input=textwrap.dedent("""\
                {
                  "extractions": [
                    {"person": "Albert Einstein", "person_attributes": {"field": "physics"}}
                  ]
                }"""),
        fence_output=True,
        strict_fences=False,
        expected_key="person",
        expected_value="Albert Einstein",
    )

  def test_no_fence_expectation(self):
    self._test_parsing_scenario(
        test_input=textwrap.dedent("""\
                {
                  "extractions": [
                    {"drug": "Aspirin", "drug_attributes": {"dosage": "100mg"}}
                  ]
                }"""),
        fence_output=False,
        strict_fences=False,
        expected_key="drug",
        expected_value="Aspirin",
    )

  def test_fallback_preserves_content_integrity(self):
    test_input = textwrap.dedent("""\
            {
              "extractions": [
                {
                  "medication": "Ibuprofen",
                  "medication_attributes": {
                    "dosage": "200mg",
                    "frequency": "twice daily"
                  }
                },
                {
                  "condition": "headache",
                  "condition_attributes": {
                    "severity": "mild"
                  }
                }
              ]
            }""")
    resolver = resolver_lib.Resolver(
        fence_output=True,
        format_type=data.FormatType.JSON,
        strict_fences=False,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(
        len(result), 2, "Should preserve all extractions during fallback"
    )

    self.assertEqual(
        result[0]["medication"],
        "Ibuprofen",
        "First extraction should have correct medication",
    )
    self.assertEqual(
        result[0]["medication_attributes"]["dosage"],
        "200mg",
        "Should preserve nested attributes in fallback",
    )

    self.assertEqual(
        result[1]["condition"],
        "headache",
        "Second extraction should have correct condition",
    )
    self.assertEqual(
        result[1]["condition_attributes"]["severity"],
        "mild",
        "Should preserve all nested attributes",
    )

  def test_malformed_json_still_raises_error(self):
    test_input = textwrap.dedent("""\
            {
              "extractions": [
                {"person": "Missing closing brace"
              ]""")
    resolver = resolver_lib.Resolver(
        fence_output=True,
        format_type=data.FormatType.JSON,
        strict_fences=False,
    )
    with self.assertRaises(resolver_lib.ResolverParsingError):
      resolver.string_to_extraction_data(test_input)

  def test_strict_fences_raises_on_missing_markers(self):
    strict_resolver = resolver_lib.Resolver(
        fence_output=True,
        format_type=data.FormatType.JSON,
        strict_fences=True,
    )
    test_input = textwrap.dedent("""\
            {"extractions": [{"person": "Test"}]}""")

    with self.assertRaisesRegex(
        resolver_lib.ResolverParsingError, ".*fence markers.*"
    ):
      strict_resolver.string_to_extraction_data(test_input)

  def test_default_allows_fallback(self):
    default_resolver = resolver_lib.Resolver(
        fence_output=True,
        format_type=data.FormatType.JSON,
    )
    test_input = textwrap.dedent("""\
            {"extractions": [{"person": "Default Test"}]}""")

    result = default_resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]["person"], "Default Test")

  def test_rejects_multiple_fenced_blocks(self):
    test_input = textwrap.dedent("""\
            preamble
            ```json
            {"extractions": [{"item": "first"}]}
            ```
            Some explanation text
            ```json
            {"extractions": [{"item": "second"}]}
            ```""")
    resolver = resolver_lib.Resolver(
        fence_output=True,
        format_type=data.FormatType.JSON,
        strict_fences=False,
    )
    with self.assertRaisesRegex(
        resolver_lib.ResolverParsingError, "Multiple fenced blocks found"
    ):
      resolver.string_to_extraction_data(test_input)


class FlexibleSchemaTest(unittest.TestCase):
  """Tests for flexible schema formats without extractions key."""

  def test_direct_list_format(self):
    test_input = textwrap.dedent("""\
            [
              {"person": "Marie Curie", "field": "physics"},
              {"person": "Albert Einstein", "field": "relativity"}
            ]""")
    resolver = resolver_lib.Resolver(
        fence_output=False,
        format_type=data.FormatType.JSON,
        require_extractions_key=False,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0]["person"], "Marie Curie")
    self.assertEqual(result[1]["person"], "Albert Einstein")

  def test_single_dict_as_extraction(self):
    test_input = '{"person": "Isaac Newton", "field": "gravity"}'
    resolver = resolver_lib.Resolver(
        fence_output=False,
        format_type=data.FormatType.JSON,
        require_extractions_key=False,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]["person"], "Isaac Newton")
    self.assertEqual(result[0]["field"], "gravity")

  def test_traditional_format_still_works(self):
    test_input = textwrap.dedent("""\
            {
              "extractions": [
                {"person": "Charles Darwin", "field": "evolution"}
              ]
            }""")
    resolver = resolver_lib.Resolver(
        fence_output=False,
        format_type=data.FormatType.JSON,
        require_extractions_key=False,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]["person"], "Charles Darwin")

  def test_strict_mode_rejects_list(self):
    test_input = '[{"person": "Test"}]'
    resolver = resolver_lib.Resolver(
        fence_output=False,
        format_type=data.FormatType.JSON,
        require_extractions_key=True,
    )
    with self.assertRaisesRegex(
        resolver_lib.ResolverParsingError, ".*must be a mapping.*"
    ):
      resolver.string_to_extraction_data(test_input)

  def test_flexible_with_attributes(self):
    test_input = textwrap.dedent("""\
            [
              {
                "medication": "Aspirin",
                "medication_attributes": {"dosage": "100mg", "frequency": "daily"}
              },
              {
                "medication": "Ibuprofen",
                "medication_attributes": {"dosage": "200mg"}
              }
            ]""")
    resolver = resolver_lib.Resolver(
        fence_output=False,
        format_type=data.FormatType.JSON,
        require_extractions_key=False,
    )
    result = resolver.string_to_extraction_data(test_input)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0]["medication"], "Aspirin")
    self.assertEqual(result[0]["medication_attributes"]["dosage"], "100mg")
    self.assertEqual(result[1]["medication"], "Ibuprofen")


if __name__ == "__main__":
  unittest.main()
