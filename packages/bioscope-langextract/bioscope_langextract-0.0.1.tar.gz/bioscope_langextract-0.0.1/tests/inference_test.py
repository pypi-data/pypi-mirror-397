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

"""Tests for inference module.

Note: This file contains test helper classes that intentionally have
few public methods and define attributes outside __init__. These
pylint warnings are expected for test fixtures.
"""
# pylint: disable=attribute-defined-outside-init

import unittest

from langextract.core import base_model


class TestBaseLanguageModel(unittest.TestCase):

  def test_merge_kwargs_with_none(self):
    """Test merge_kwargs handles None runtime_kwargs."""

    class TestModel(base_model.BaseLanguageModel):  # pylint: disable=too-few-public-methods

      def infer(self, batch_prompts, **kwargs):
        return iter([])

    model = TestModel()
    model._extra_kwargs = {"a": 1, "b": 2}

    result = model.merge_kwargs(None)
    self.assertEqual(
        {"a": 1, "b": 2},
        result,
        "merge_kwargs(None) should return stored kwargs unchanged",
    )

    result = model.merge_kwargs({})
    self.assertEqual(
        {"a": 1, "b": 2},
        result,
        "merge_kwargs({}) should return stored kwargs unchanged",
    )

  def test_merge_kwargs_override(self):
    """Test merge_kwargs allows runtime override."""

    class TestModel(base_model.BaseLanguageModel):  # pylint: disable=too-few-public-methods

      def infer(self, batch_prompts, **kwargs):
        return iter([])

    model = TestModel()
    model._extra_kwargs = {"a": 1, "b": 2}

    result = model.merge_kwargs({"b": 99, "c": 3})
    self.assertEqual(
        {"a": 1, "b": 99, "c": 3},
        result,
        "runtime kwargs should override stored kwargs",
    )

  def test_merge_kwargs_without_extra_kwargs(self):
    """Test merge_kwargs when _extra_kwargs is missing or None."""

    class TestModel(base_model.BaseLanguageModel):  # pylint: disable=too-few-public-methods

      def infer(self, batch_prompts, **kwargs):
        return iter([])

    model = TestModel()
    model._extra_kwargs = None

    result = model.merge_kwargs({"x": 10})
    self.assertEqual(
        {"x": 10},
        result,
        "merge_kwargs should work even without _extra_kwargs attribute",
    )


if __name__ == "__main__":
  unittest.main()
