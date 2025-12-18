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

from langextract.core import tokenizer


class TokenizerTest(unittest.TestCase):

  def assertTokenListEqual(self, actual_tokens, expected_tokens, msg=None):
    self.assertEqual(len(actual_tokens), len(expected_tokens), msg=msg)
    for i, (expected, actual) in enumerate(zip(expected_tokens, actual_tokens)):
      expected_normalized = tokenizer.Token(
          index=expected.index,
          token_type=expected.token_type,
          first_token_after_newline=expected.first_token_after_newline,
      )
      actual_normalized = tokenizer.Token(
          index=actual.index,
          token_type=actual.token_type,
          first_token_after_newline=actual.first_token_after_newline,
      )
      self.assertEqual(
          expected_normalized,
          actual_normalized,
          msg=f"Token mismatch at index {i}",
      )

  def test_tokenize_basic_text(self):
    input_text = "Hello, world!"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_multiple_spaces_and_numbers(self):
    input_text = "Age:   25\nWeight=70kg."
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(
            index=3,
            token_type=tokenizer.TokenType.WORD,
            first_token_after_newline=True,
        ),
        tokenizer.Token(index=4, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=5, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(index=6, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=7, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_multi_line_input(self):
    input_text = "Line1\nLine2\nLine3"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(
            index=2,
            token_type=tokenizer.TokenType.WORD,
            first_token_after_newline=True,
        ),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(
            index=4,
            token_type=tokenizer.TokenType.WORD,
            first_token_after_newline=True,
        ),
        tokenizer.Token(index=5, token_type=tokenizer.TokenType.NUMBER),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_only_symbols(self):
    input_text = "!!!@#   $$$%"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=4, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_empty_string(self):
    input_text = ""
    expected_tokens = []
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_non_ascii_text(self):
    input_text = "café"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_mixed_punctuation(self):
    input_text = "?!"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tokenized = tokenizer.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_first_token_after_newline_flag(self):
    input_text = "Line1\nLine2\nLine3"
    tokenized = tokenizer.tokenize(input_text)

    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(
            index=2,
            token_type=tokenizer.TokenType.WORD,
            first_token_after_newline=True,
        ),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.NUMBER),
        tokenizer.Token(
            index=4,
            token_type=tokenizer.TokenType.WORD,
            first_token_after_newline=True,
        ),
        tokenizer.Token(index=5, token_type=tokenizer.TokenType.NUMBER),
    ]

    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg="Newline flags mismatch",
    )

  def test_performance_optimization_no_crash(self):
    """Verify that tokenization handles empty strings and newlines without error."""
    tok = tokenizer.RegexTokenizer()
    text = ""
    tokenized = tok.tokenize(text)
    self.assertEqual(len(tokenized.tokens), 0)

    text = "\n"
    tokenized = tok.tokenize(text)
    self.assertEqual(len(tokenized.tokens), 0)

    text = "A\nB"
    tokenized = tok.tokenize(text)
    self.assertEqual(len(tokenized.tokens), 2)
    self.assertTrue(tokenized.tokens[1].first_token_after_newline)

  def test_underscore_handling(self):
    """Verify that underscores are preserved as punctuation/symbols."""
    tok = tokenizer.RegexTokenizer()
    text = "user_id"
    tokenized = tok.tokenize(text)
    # Expecting: "user", "_", "id"
    self.assertEqual(len(tokenized.tokens), 3)
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)
    self.assertEqual(
        tokenized.tokens[1].token_type, tokenizer.TokenType.PUNCTUATION
    )
    self.assertEqual(tokenized.tokens[2].token_type, tokenizer.TokenType.WORD)


class UnicodeTokenizerTest(unittest.TestCase):

  def assertTokenListEqual(self, actual_tokens, expected_tokens, msg=None):
    self.assertEqual(len(actual_tokens), len(expected_tokens), msg=msg)
    for i, (expected, actual) in enumerate(zip(expected_tokens, actual_tokens)):
      expected_tok = tokenizer.Token(
          index=expected.index,
          token_type=expected.token_type,
          first_token_after_newline=expected.first_token_after_newline,
      )
      actual_tok = tokenizer.Token(
          index=actual.index,
          token_type=actual.token_type,
          first_token_after_newline=actual.first_token_after_newline,
      )
      self.assertEqual(
          expected_tok,
          actual_tok,
          msg=f"Token mismatch at index {i}",
      )

  def test_tokenize_japanese_text(self):
    input_text = "こんにちは、世界！"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=4, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=5, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=6, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=7, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=8, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_english_text(self):
    input_text = "Hello, world!"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.PUNCTUATION),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.PUNCTUATION),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_tokenize_mixed_text(self):
    input_text = "Hello 世界 123"
    expected_tokens = [
        tokenizer.Token(index=0, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=1, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=2, token_type=tokenizer.TokenType.WORD),
        tokenizer.Token(index=3, token_type=tokenizer.TokenType.NUMBER),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertTokenListEqual(
        tokenized.tokens,
        expected_tokens,
        msg=f"Tokens mismatch for input: {input_text!r}",
    )

  def test_mixed_digit_han_same_type_grouping(self):
    """Test mixed digit and Han characters."""
    input_text = "10毫克"  # "10 milligrams"
    expected_tokens = [
        ("10", tokenizer.TokenType.NUMBER),
        ("毫", tokenizer.TokenType.WORD),
        ("克", tokenizer.TokenType.WORD),
    ]
    expected_first_after_newline = [False, False, False]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (
        token,
        (expected_text, expected_type),
        expected_newline,
    ) in enumerate(
        zip(tokenized.tokens, expected_tokens, expected_first_after_newline)
    ):
      actual_text = input_text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(
          actual_text, expected_text, msg=f"Token {i} text mismatch."
      )
      self.assertEqual(
          token.token_type, expected_type, msg=f"Token {i} type mismatch."
      )
      self.assertEqual(
          token.first_token_after_newline,
          expected_newline,
          msg=f"Token {i} newline flag mismatch.",
      )

  def test_underscore_word_separator(self):
    """Test underscore as word separator."""
    input_text = "hello_world"
    expected_tokens = [
        ("hello", tokenizer.TokenType.WORD),
        ("_", tokenizer.TokenType.PUNCTUATION),
        ("world", tokenizer.TokenType.WORD),
    ]
    expected_first_after_newline = [False, False, False]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (
        token,
        (expected_text, expected_type),
        expected_newline,
    ) in enumerate(
        zip(tokenized.tokens, expected_tokens, expected_first_after_newline)
    ):
      actual_text = input_text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(
          actual_text, expected_text, msg=f"Token {i} text mismatch."
      )
      self.assertEqual(
          token.token_type, expected_type, msg=f"Token {i} type mismatch."
      )
      self.assertEqual(
          token.first_token_after_newline,
          expected_newline,
          msg=f"Token {i} newline flag mismatch.",
      )

  def test_leading_trailing_underscores(self):
    """Test leading and trailing underscores."""
    input_text = "_test_case_"
    expected_tokens = [
        ("_", tokenizer.TokenType.PUNCTUATION),
        ("test", tokenizer.TokenType.WORD),
        ("_", tokenizer.TokenType.PUNCTUATION),
        ("case", tokenizer.TokenType.WORD),
        ("_", tokenizer.TokenType.PUNCTUATION),
    ]
    expected_first_after_newline = [False, False, False, False, False]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (
        token,
        (expected_text, expected_type),
        expected_newline,
    ) in enumerate(
        zip(tokenized.tokens, expected_tokens, expected_first_after_newline)
    ):
      actual_text = input_text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(
          actual_text, expected_text, msg=f"Token {i} text mismatch."
      )
      self.assertEqual(
          token.token_type, expected_type, msg=f"Token {i} type mismatch."
      )
      self.assertEqual(
          token.first_token_after_newline,
          expected_newline,
          msg=f"Token {i} newline flag mismatch.",
      )

  def test_first_token_after_newline_parity(self):
    """Test that UnicodeTokenizer matches RegexTokenizer for newline detection."""
    input_text = "a\n b"
    regex_tok = tokenizer.RegexTokenizer()
    regex_tokens = regex_tok.tokenize(input_text).tokens
    self.assertTrue(regex_tokens[1].first_token_after_newline)

    unicode_tok = tokenizer.UnicodeTokenizer()
    unicode_tokens = unicode_tok.tokenize(input_text).tokens
    self.assertTrue(
        unicode_tokens[1].first_token_after_newline,
        "UnicodeTokenizer failed to detect newline in gap 'a\\n b'",
    )

  def test_expanded_cjk_detection(self):
    """Test detection of CJK characters in extended ranges."""
    input_text = "\u4e00\u3400\U00020000"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)

    self.assertEqual(len(tokenized.tokens), 3)
    for token in tokenized.tokens:
      self.assertEqual(token.token_type, tokenizer.TokenType.WORD)

  def test_mixed_script_and_emoji(self):
    """Test mixed script and emoji handling."""
    input_text = "Hello👋🏼世界123"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)

    expected_tokens = [
        ("Hello", tokenizer.TokenType.WORD),
        ("👋🏼", tokenizer.TokenType.PUNCTUATION),
        ("世", tokenizer.TokenType.WORD),
        ("界", tokenizer.TokenType.WORD),
        ("123", tokenizer.TokenType.NUMBER),
    ]

    self.assertEqual(len(tokenized.tokens), len(expected_tokens))
    for i, (expected_text, expected_type) in enumerate(expected_tokens):
      token = tokenized.tokens[i]
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_script_boundary_grouping(self):
    """Test that we do NOT group characters from different scripts."""
    tok = tokenizer.UnicodeTokenizer()
    text = "HelloПривет"
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 2, "Should be split into 2 tokens")
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)
    self.assertEqual(tokenized.tokens[1].token_type, tokenizer.TokenType.WORD)

    t1_text = text[
        tokenized.tokens[0]
        .char_interval.start_pos : tokenized.tokens[0]
        .char_interval.end_pos
    ]
    t2_text = text[
        tokenized.tokens[1]
        .char_interval.start_pos : tokenized.tokens[1]
        .char_interval.end_pos
    ]

    self.assertEqual(t1_text, "Hello")
    self.assertEqual(t2_text, "Привет")

  def test_non_spaced_scripts_no_grouping(self):
    """Test that non-spaced scripts (Thai, Lao, etc.) are NOT grouped into a single word."""
    tok = tokenizer.UnicodeTokenizer()
    text = "สวัสดี"
    tokenized = tok.tokenize(text)

    self.assertGreater(
        len(tokenized.tokens), 1, "Should not be grouped into a single token"
    )
    self.assertEqual(len(tokenized.tokens), 4)

  def test_cjk_detection_regex(self):
    """Test that CJK characters are detected and not grouped."""
    tok = tokenizer.UnicodeTokenizer()
    text = "你好"
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 2)
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)
    self.assertEqual(tokenized.tokens[1].token_type, tokenizer.TokenType.WORD)

  def test_newline_simplification(self):
    """Test that newline handling works correctly with the simplified logic."""
    tok = tokenizer.UnicodeTokenizer()
    text = "LineA\nLineB"
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 2)
    self.assertEqual(tokenized.tokens[0].first_token_after_newline, False)
    self.assertTrue(tokenized.tokens[1].first_token_after_newline)

  def test_newline_simplification_start(self):
    """Test newline at start of text."""
    tok = tokenizer.UnicodeTokenizer()
    text = "\nLineA"
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 1)
    self.assertTrue(tokenized.tokens[0].first_token_after_newline)

  def test_mixed_line_endings(self):
    """Test mixed line endings (\\r\\n)."""
    text = "LineOne\r\nLineTwo"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(text)
    self.assertEqual(len(tokenized.tokens), 2)
    self.assertTrue(tokenized.tokens[1].first_token_after_newline)

  def test_mixed_uncommon_scripts_no_grouping(self):
    """Test that adjacent unknown scripts are NOT merged."""
    tok = tokenizer.UnicodeTokenizer()
    # Armenian "Բարև" + Georgian "გამარჯობა".
    # Both are "unknown" to _COMMON_SCRIPTS, so should not be grouped together.
    text = "Բարևგამარჯობა"
    tokenized = tok.tokenize(text)

    # Unknown scripts are fragmented into characters for safety.
    self.assertEqual(
        len(tokenized.tokens),
        13,
        "Should be fragmented into characters for safety (13 tokens)",
    )
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)
    self.assertEqual(tokenized.tokens[1].token_type, tokenizer.TokenType.WORD)

  def test_unknown_script_merging_edge_case(self):
    """Verify that adjacent IDENTICAL unknown scripts are fragmented for safety."""
    # Armenian "Բարև" + Armenian "Բარև".
    tok = tokenizer.UnicodeTokenizer()
    text = "ԲარևԲარև"
    tokenized = tok.tokenize(text)
    # Should be fragmented into 8 characters
    self.assertEqual(len(tokenized.tokens), 8)
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)

  def test_find_sentence_range_empty_input(self):
    """Ensure robustness against empty input."""
    interval = tokenizer.find_sentence_range("", [], 0)
    self.assertEqual(interval, tokenizer.TokenInterval(0, 0))

  def test_normalization_indices_match_input(self):
    """Test that token indices match the ORIGINAL input, not normalized text."""
    nfd_text = "e\u0301"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(nfd_text)

    self.assertEqual(tokenized.text, nfd_text)
    self.assertEqual(len(tokenized.tokens), 1)
    self.assertEqual(tokenized.tokens[0].char_interval.start_pos, 0)
    self.assertEqual(tokenized.tokens[0].char_interval.end_pos, 2)

  def test_acronym_inconsistency(self):
    """Test that RegexTokenizer does NOT produce ACRONYM tokens (standardization)."""
    tok = tokenizer.RegexTokenizer()
    text = "A/B"
    tokenized = tok.tokenize(text)
    self.assertEqual(len(tokenized.tokens), 3)
    self.assertEqual(tokenized.tokens[0].token_type, tokenizer.TokenType.WORD)
    self.assertEqual(
        tokenized.tokens[1].token_type, tokenizer.TokenType.PUNCTUATION
    )
    self.assertEqual(tokenized.tokens[2].token_type, tokenizer.TokenType.WORD)

  def test_consecutive_punctuation_grouping(self):
    """Test that consecutive punctuation is grouped into a single token."""
    input_text = "Hello!! World..."
    expected_tokens = ["Hello", "!!", "World", "..."]
    tokens = tokenizer.UnicodeTokenizer().tokenize(input_text).tokens
    self.assertEqual(
        [
            input_text[t.char_interval.start_pos : t.char_interval.end_pos]
            for t in tokens
        ],
        expected_tokens,
    )

  def test_punctuation_merging_identical_only(self):
    """Test that only identical punctuation is merged."""
    input_text = "Hello!! World..."
    expected_tokens = ["Hello", "!!", "World", "..."]
    tokens = tokenizer.UnicodeTokenizer().tokenize(input_text).tokens
    self.assertEqual(
        [
            input_text[t.char_interval.start_pos : t.char_interval.end_pos]
            for t in tokens
        ],
        expected_tokens,
    )

    input_text_mixed = 'End."'
    expected_tokens_mixed = ["End", ".", '"']
    tokens_mixed = (
        tokenizer.UnicodeTokenizer().tokenize(input_text_mixed).tokens
    )
    self.assertEqual(
        [
            input_text_mixed[
                t.char_interval.start_pos : t.char_interval.end_pos
            ]
            for t in tokens_mixed
        ],
        expected_tokens_mixed,
    )

  def test_distinct_unknown_scripts_do_not_merge(self):
    """Verify that distinct unknown scripts are not merged."""
    text = "অअ"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 2)
    self.assertEqual(tokenized.tokens[0].char_interval.start_pos, 0)
    self.assertEqual(tokenized.tokens[0].char_interval.end_pos, 1)
    self.assertEqual(tokenized.tokens[1].char_interval.start_pos, 1)
    self.assertEqual(tokenized.tokens[1].char_interval.end_pos, 2)

  def test_identical_unknown_scripts_merge(self):
    """Verify that identical unknown scripts merge into a single token."""
    text = "অআ"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(text)

    self.assertEqual(len(tokenized.tokens), 2)
    self.assertEqual(tokenized.tokens[0].char_interval.start_pos, 0)
    self.assertEqual(tokenized.tokens[0].char_interval.end_pos, 1)
    self.assertEqual(tokenized.tokens[1].char_interval.start_pos, 1)
    self.assertEqual(tokenized.tokens[1].char_interval.end_pos, 2)


class ExceptionTest(unittest.TestCase):
  """Test custom exception types and error conditions."""

  def test_invalid_token_interval_errors(self):
    """Test that InvalidTokenIntervalError is raised for invalid intervals."""
    text = "Hello, world!"
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(text)

    with self.assertRaisesRegex(
        tokenizer.InvalidTokenIntervalError,
        "Invalid token interval.*start_index=-1",
    ):
      tokenizer.tokens_text(
          tokenized, tokenizer.TokenInterval(start_index=-1, end_index=1)
      )

    with self.assertRaisesRegex(
        tokenizer.InvalidTokenIntervalError,
        "Invalid token interval.*end_index=999",
    ):
      tokenizer.tokens_text(
          tokenized, tokenizer.TokenInterval(start_index=0, end_index=999)
      )

    with self.assertRaisesRegex(
        tokenizer.InvalidTokenIntervalError,
        "Invalid token interval.*start_index=2.*end_index=1",
    ):
      tokenizer.tokens_text(
          tokenized, tokenizer.TokenInterval(start_index=2, end_index=1)
      )

  def test_sentence_range_errors(self):
    """Test that SentenceRangeError is raised for invalid start positions."""
    text = "Hello world."
    tok = tokenizer.UnicodeTokenizer()
    tokens = tok.tokenize(text).tokens

    with self.assertRaisesRegex(
        tokenizer.SentenceRangeError, "start_token_index=-1 out of range"
    ):
      tokenizer.find_sentence_range(text, tokens, -1)

    with self.assertRaisesRegex(
        tokenizer.SentenceRangeError,
        "start_token_index=999 out of range.*Total tokens: 3",
    ):
      tokenizer.find_sentence_range(text, tokens, 999)

    # Empty input should NOT raise SentenceRangeError
    interval = tokenizer.find_sentence_range("", [], 0)
    self.assertEqual(interval, tokenizer.TokenInterval(0, 0))


class NegativeTestCases(unittest.TestCase):
  """Test cases for invalid input and edge cases."""

  def test_invalid_utf8_sequence(self):
    input_text = "Invalid \ufffd sequence"
    expected_tokens = [
        ("Invalid", tokenizer.TokenType.WORD),
        ("\ufffd", tokenizer.TokenType.PUNCTUATION),
        ("sequence", tokenizer.TokenType.WORD),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (token, (expected_text, expected_type)) in enumerate(
        zip(tokenized.tokens, expected_tokens)
    ):
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_extremely_long_grapheme_cluster(self):
    input_text = "e" + "\u0301" * 10
    expected_tokens = [("e" + "\u0301" * 10, tokenizer.TokenType.WORD)]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (token, (expected_text, expected_type)) in enumerate(
        zip(tokenized.tokens, expected_tokens)
    ):
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_mixed_valid_invalid_unicode(self):
    input_text = "Valid текст \ufffd 中文"
    expected_tokens = [
        ("Valid", tokenizer.TokenType.WORD),
        ("текст", tokenizer.TokenType.WORD),
        ("\ufffd", tokenizer.TokenType.PUNCTUATION),
        ("中", tokenizer.TokenType.WORD),
        ("文", tokenizer.TokenType.WORD),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (token, (expected_text, expected_type)) in enumerate(
        zip(tokenized.tokens, expected_tokens)
    ):
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_zero_width_joiners(self):
    input_text = "Family: 👨‍👩‍👧‍👦"
    expected_tokens = [
        ("Family", tokenizer.TokenType.WORD),
        (":", tokenizer.TokenType.PUNCTUATION),
        ("👨‍👩‍👧‍👦", tokenizer.TokenType.PUNCTUATION),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (token, (expected_text, expected_type)) in enumerate(
        zip(tokenized.tokens, expected_tokens)
    ):
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_isolated_combining_marks(self):
    input_text = "\u0301\u0302\u0303 test"
    expected_tokens = [
        ("\u0301\u0302\u0303", tokenizer.TokenType.PUNCTUATION),
        ("test", tokenizer.TokenType.WORD),
    ]
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize(input_text)
    self.assertEqual(len(tokenized.tokens), len(expected_tokens))

    for i, (token, (expected_text, expected_type)) in enumerate(
        zip(tokenized.tokens, expected_tokens)
    ):
      actual_text = tokenized.text[
          token.char_interval.start_pos : token.char_interval.end_pos
      ]
      self.assertEqual(actual_text, expected_text)
      self.assertEqual(token.token_type, expected_type)

  def test_empty_string_edge_case(self):
    tok = tokenizer.UnicodeTokenizer()
    tokenized = tok.tokenize("")
    self.assertEqual(
        len(tokenized.tokens), 0, "Empty string should produce no tokens"
    )
    self.assertEqual(
        tokenized.text, "", "Tokenized text should preserve empty string"
    )

  def test_whitespace_only_string(self):
    tok = tokenizer.UnicodeTokenizer()
    test_cases = [
        "   ",  # Spaces
        "\t\t",  # Tabs
        "\n\n",  # Newlines
        " \t\n\r ",  # Mixed whitespace
    ]
    for whitespace in test_cases:
      tokenized = tok.tokenize(whitespace)
      self.assertEqual(
          len(tokenized.tokens),
          0,
          f"Whitespace-only string '{repr(whitespace)}' should produce no"
          " tokens",
      )


class TokensTextTest(unittest.TestCase):

  _SENTENCE_WITH_ONE_LINE = "Patient Jane Doe, ID 67890, received 10mg daily."

  def test_substring_jane_doe(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=1, end_index=3)
    result_str = tokenizer.tokens_text(input_tokenized, interval)
    self.assertEqual(result_str, "Jane Doe")

  def test_substring_with_punctuation(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=0, end_index=4)
    result_str = tokenizer.tokens_text(input_tokenized, interval)
    self.assertEqual(result_str, "Patient Jane Doe,")

  def test_numeric_tokens(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=5, end_index=6)
    result_str = tokenizer.tokens_text(input_tokenized, interval)
    self.assertEqual(result_str, "67890")

  def test_start_index_negative(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=-1, end_index=2)
    with self.assertRaises(tokenizer.InvalidTokenIntervalError):
      tokenizer.tokens_text(input_tokenized, interval)

  def test_end_index_out_of_bounds(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=0, end_index=999)
    with self.assertRaises(tokenizer.InvalidTokenIntervalError):
      tokenizer.tokens_text(input_tokenized, interval)

  def test_start_index_gt_end_index(self):
    input_tokenized = tokenizer.tokenize(self._SENTENCE_WITH_ONE_LINE)
    interval = tokenizer.TokenInterval(start_index=5, end_index=4)
    with self.assertRaises(tokenizer.InvalidTokenIntervalError):
      tokenizer.tokens_text(input_tokenized, interval)


class SentenceRangeTest(unittest.TestCase):

  def test_simple_sentence(self):
    input_text = "This is one sentence. Then another?"
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    interval = tokenizer.find_sentence_range(input_text, tokens, 0)
    self.assertEqual(interval.start_index, 0)
    self.assertEqual(interval.end_index, 5)

  def test_abbreviation_not_boundary(self):
    input_text = "Dr. John visited. Then left."
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    interval = tokenizer.find_sentence_range(input_text, tokens, 0)
    self.assertEqual(interval.start_index, 0)
    self.assertEqual(interval.end_index, 5)

  def test_second_line_capital_letter_terminates_sentence(self):
    input_text = textwrap.dedent("""\
            Blood pressure was 160/90 and patient was recommended to
            Atenolol 50 mg daily.""")
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    interval = tokenizer.find_sentence_range(input_text, tokens, 0)
    self.assertEqual(interval.start_index, 0)
    self.assertEqual(interval.end_index, 11)

  def test_full_sentence_range_end_of_text(self):
    input_text = "Only one sentence here"
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    interval = tokenizer.find_sentence_range(input_text, tokens, 0)
    self.assertEqual(interval.start_index, 0)
    self.assertEqual(len(tokens), interval.end_index)

  def test_out_of_range_negative_start(self):
    input_text = "Hello world."
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    with self.assertRaises(tokenizer.SentenceRangeError):
      tokenizer.find_sentence_range(input_text, tokens, -1)

  def test_out_of_range_exceeding_length(self):
    input_text = "Hello world."
    tokenized = tokenizer.tokenize(input_text)
    tokens = tokenized.tokens
    with self.assertRaises(tokenizer.SentenceRangeError):
      tokenizer.find_sentence_range(input_text, tokens, 999)

  def test_sentence_boundary_with_quote(self):
    """Test that sentence boundary detection works with trailing quotes."""
    text = 'He said "Hello."'
    tokens = tokenizer.UnicodeTokenizer().tokenize(text).tokens
    interval = tokenizer.find_sentence_range(text, tokens, 0)
    self.assertEqual(interval.end_index, len(tokens))

  def test_sentence_splitting_permissive(self):
    """Test permissive sentence splitting (quotes, numbers, \\r)."""
    # Quote-initiated sentence.
    text_quote = '"The time is now." Next sentence.'
    tokens = tokenizer.UnicodeTokenizer().tokenize(text_quote).tokens
    interval = tokenizer.find_sentence_range(text_quote, tokens, 0)
    self.assertEqual(interval.end_index, 7)

    # Number-initiated sentence.
    text_number = "2025 will be good. Really."
    tokens = tokenizer.tokenize(text_number).tokens
    interval = tokenizer.find_sentence_range(text_number, tokens, 0)
    self.assertEqual(interval.end_index, 5)

    # Carriage return support.
    text_cr = "Line one.\rLine two."
    tokens = tokenizer.tokenize(text_cr).tokens
    interval = tokenizer.find_sentence_range(text_cr, tokens, 0)
    self.assertEqual(interval.end_index, 3)

  def test_unicode_sentence_boundaries(self):
    """Verify that Unicode sentence terminators are respected."""
    # Japanese full stop
    text_jp = "こんにちは。世界。"
    tokens = tokenizer.UnicodeTokenizer().tokenize(text_jp).tokens
    interval = tokenizer.find_sentence_range(text_jp, tokens, 0)
    self.assertEqual(interval.end_index, 6)

    # Hindi Danda
    text_hi = "नमस्ते। दुनिया।"
    tokens = tokenizer.UnicodeTokenizer().tokenize(text_hi).tokens
    interval = tokenizer.find_sentence_range(text_hi, tokens, 0)
    self.assertEqual(interval.end_index, 2)

  def test_configurable_sentence_splitting(self):
    """Verify that custom abbreviations prevent sentence splitting."""
    tok = tokenizer.RegexTokenizer()

    text_french = "M. Smith est ici."
    tokenized_french = tok.tokenize(text_french)

    # Default: "M." ends sentence.
    sentence1 = tokenizer.find_sentence_range(
        text_french, tokenized_french.tokens, 0
    )
    self.assertEqual(sentence1.end_index, 2)

    # Now with custom abbreviations
    custom_abbrevs = {"M."}
    sentence2 = tokenizer.find_sentence_range(
        text_french,
        tokenized_french.tokens,
        0,
        known_abbreviations=custom_abbrevs,
    )

    # Should NOT split at "M."
    self.assertEqual(sentence2.end_index, 6)


if __name__ == "__main__":
  unittest.main()
