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

"""Tests for the schema module.

Note: This file contains test helper classes that intentionally have
few public methods. The too-few-public-methods warnings are expected.
"""

import unittest
from unittest import mock
import warnings

from langextract.core import base_model
from langextract.core import data
from langextract.core import format_handler as fh
from langextract.core import schema


class BaseSchemaTest(unittest.TestCase):
  """Tests for BaseSchema abstract class."""

  def test_abstract_methods_required(self):
    """Test that BaseSchema cannot be instantiated directly."""
    with self.assertRaises(TypeError):
      schema.BaseSchema()  # pylint: disable=abstract-class-instantiated

  def test_subclass_must_implement_all_methods(self):
    """Test that subclasses must implement all abstract methods."""

    class IncompleteSchema(schema.BaseSchema):  # pylint: disable=too-few-public-methods

      @classmethod
      def from_examples(cls, examples_data, attribute_suffix="_attributes"):
        return cls()

    with self.assertRaises(TypeError):
      IncompleteSchema()  # pylint: disable=abstract-class-instantiated


class BaseLanguageModelSchemaTest(unittest.TestCase):
  """Tests for BaseLanguageModel schema methods."""

  def test_get_schema_class_returns_none_by_default(self):
    """Test that get_schema_class returns None by default."""

    class TestModel(base_model.BaseLanguageModel):  # pylint: disable=too-few-public-methods

      def infer(self, batch_prompts, **kwargs):
        yield []

    self.assertIsNone(TestModel.get_schema_class())

  def test_apply_schema_stores_instance(self):
    """Test that apply_schema stores the schema instance."""

    class TestModel(base_model.BaseLanguageModel):  # pylint: disable=too-few-public-methods

      def infer(self, batch_prompts, **kwargs):
        yield []

    model = TestModel()

    mock_schema = mock.Mock(spec=schema.BaseSchema)

    model.apply_schema(mock_schema)

    self.assertEqual(model._schema, mock_schema)

    model.apply_schema(None)
    self.assertIsNone(model._schema)


class FormatModeSchemaTest(unittest.TestCase):
  """Tests for FormatModeSchema."""

  def test_base_schema_no_validation(self):
    """Test that FormatModeSchema has no validation by default."""
    schema_obj = schema.FormatModeSchema()
    format_handler = fh.FormatHandler(
        format_type=data.FormatType.JSON,
        use_fences=True,
    )

    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter("always")
      schema_obj.validate_format(format_handler)

      self.assertEqual(
          len(w), 0, "FormatModeSchema should not issue validation warnings"
      )


if __name__ == "__main__":
  unittest.main()
