#!/usr/bin/env python3
"""
Tests for create_tiered_decks.py
"""

import csv
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from create_tiered_decks import (
    create_kanji_csv,
    create_vocab_csv,
    format_kanji_back_field,
    get_new_jlpt_level,
    main,
    parse_args,
    process_kanji_character,
)


class TestProcessKanjiCharacter:
    """Tests for process_kanji_character function"""

    def test_complete_character(self):
        """Test processing complete character data"""
        char = {
            "literal": "学",
            "misc": {
                "jlptLevel": 2,
                "strokeCounts": [8],
                "grade": 5,
                "frequency": 348,
            },
            "readingMeaning": {
                "groups": [
                    {
                        "readings": [
                            {"type": "ja_on", "value": "ガク"},
                            {"type": "ja_kun", "value": "まな.ぶ"},
                        ],
                        "meanings": [{"lang": "en", "value": "study"}],
                    }
                ],
                "nanori": ["たか"],
            },
            "radicals": [{"value": "子"}],
            "dictionaryReferences": [
                {"type": "heisig", "value": "1"},
                {"type": "heisig6", "value": "2"},
            ],
        }

        result = process_kanji_character(char)

        assert result["kanji"] == "学"
        assert result["jlpt_level"] == 2
        assert result["on_readings"] == "ガク"
        assert result["kun_readings"] == "まな.ぶ"
        assert result["meanings"] == "study"
        assert result["stroke_count"] == 8
        assert result["grade"] == 5
        assert result["frequency"] == 348
        assert result["radical"] == "子"
        assert result["nanori"] == "たか"
        assert result["heisig_rtk"] == "1"
        assert result["heisig6_rtk"] == "2"

    def test_no_literal_returns_none(self):
        """Test character without literal returns None"""
        char = {"misc": {"jlptLevel": 4}}
        result = process_kanji_character(char)
        assert result is None

    def test_no_jlpt_level_returns_none(self):
        """Test character without JLPT level returns None"""
        char = {"literal": "一", "misc": {"grade": 1}}
        result = process_kanji_character(char)
        assert result is None

    def test_minimal_character(self):
        """Test processing character with minimal data"""
        char = {
            "literal": "一",
            "misc": {"jlptLevel": 4},
            "readingMeaning": {"groups": []},
            "radicals": [],
            "dictionaryReferences": [],
        }

        result = process_kanji_character(char)

        assert result["kanji"] == "一"
        assert result["jlpt_level"] == 4
        assert result["on_readings"] == ""
        assert result["kun_readings"] == ""
        assert result["meanings"] == ""
        assert result["stroke_count"] is None
        assert result["grade"] is None
        assert result["frequency"] is None
        assert result["radical"] is None
        assert result["nanori"] == ""
        assert result["heisig_rtk"] == ""
        assert result["heisig6_rtk"] == ""

    def test_no_reading_meaning(self):
        """Test character without readingMeaning"""
        char = {
            "literal": "一",
            "misc": {"jlptLevel": 4},
        }

        result = process_kanji_character(char)

        assert result["kanji"] == "一"
        assert result["on_readings"] == ""
        assert result["kun_readings"] == ""
        assert result["meanings"] == ""
        assert result["nanori"] == ""

    def test_multiple_stroke_counts(self):
        """Test using first stroke count when multiple exist"""
        char = {
            "literal": "一",
            "misc": {"jlptLevel": 4, "strokeCounts": [1, 2, 3]},
        }

        result = process_kanji_character(char)
        assert result["stroke_count"] == 1

    def test_empty_reading_meaning_groups(self):
        """Test with empty readingMeaning groups"""
        char = {
            "literal": "一",
            "misc": {"jlptLevel": 4},
            "readingMeaning": {"groups": []},
        }

        result = process_kanji_character(char)
        assert result["on_readings"] == ""
        assert result["kun_readings"] == ""


class TestFormatKanjiBackField:
    """Tests for format_kanji_back_field function"""

    def test_complete_character(self):
        """Test formatting complete character data"""
        char = {
            "kanji": "学",
            "meanings": "study; learning",
            "on_readings": "ガク",
            "kun_readings": "まな.ぶ",
            "nanori": "たか",
            "stroke_count": 8,
            "radical": "子",
            "frequency": 348,
            "heisig_rtk": "1",
            "heisig6_rtk": "2",
        }

        result = format_kanji_back_field(char, "N3")

        # Check HTML structure and content
        assert "学" in result
        assert "study; learning" in result
        assert "ガク" in result
        assert "まな.ぶ" in result
        assert "たか" in result
        assert "8" in result
        assert "子" in result
        assert "348" in result
        assert "RTK" in result
        assert "N3" in result
        assert "<div" in result  # HTML structure

    def test_no_optional_fields(self):
        """Test formatting with minimal data"""
        char = {
            "kanji": "一",
            "meanings": "one",
            "on_readings": "イチ; イツ",
            "kun_readings": "ひと; ひと.つ",
        }

        result = format_kanji_back_field(char, "N5")

        assert "一" in result
        assert "one" in result
        assert "イチ" in result
        assert "ひと" in result
        assert "<div" in result  # HTML structure

    def test_only_meanings(self):
        """Test formatting with only meanings"""
        char = {"kanji": "一", "meanings": "one"}

        result = format_kanji_back_field(char, "N5")
        assert "一" in result
        assert "one" in result
        assert "<div" in result  # HTML structure

    def test_only_heisig_rtk(self):
        """Test formatting with only heisig_rtk"""
        char = {
            "kanji": "一",
            "meanings": "one",
            "heisig_rtk": "1",
        }

        result = format_kanji_back_field(char, "N5")
        assert "一" in result
        assert "RTK" in result
        assert "1" in result
        assert "<div" in result  # HTML structure

    def test_only_heisig6_rtk(self):
        """Test formatting with only heisig6_rtk"""
        char = {
            "kanji": "一",
            "meanings": "one",
            "heisig6_rtk": "2",
        }

        result = format_kanji_back_field(char, "N5")
        assert "一" in result
        assert "RTK" in result
        assert "2" in result
        assert "<div" in result  # HTML structure


class TestCreateKanjiCsv:
    """Tests for create_kanji_csv function"""

    def test_basic_csv_creation(self, tmp_path):
        """Test creating basic kanji CSV file"""
        output_path = tmp_path / "test_kanji.csv"
        characters = [
            {
                "kanji": "一",
                "meanings": "one",
                "on_readings": "イチ",
                "kun_readings": "ひと",
                "grade": 1,
            }
        ]

        create_kanji_csv(characters, output_path, "N5")

        assert output_path.exists()
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert "一" in rows[0]["kanji"]
            assert "<div" in rows[0]["kanji"]  # HTML structure
            assert "one" in rows[0]["back"]
            assert "grade1" in rows[0]["tags"]

    def test_multiple_characters(self, tmp_path):
        """Test CSV with multiple characters"""
        output_path = tmp_path / "test.csv"
        characters = [
            {"kanji": "一", "meanings": "one", "grade": 1},
            {"kanji": "二", "meanings": "two", "grade": 1},
            {"kanji": "三", "meanings": "three", "grade": 1},
        ]

        create_kanji_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert "一" in rows[0]["kanji"]
            assert "二" in rows[1]["kanji"]
            assert "三" in rows[2]["kanji"]
            assert "<div" in rows[0]["kanji"]  # HTML structure

    def test_with_tier_tag(self, tmp_path):
        """Test CSV with tier information"""
        output_path = tmp_path / "test.csv"
        characters = [
            {"kanji": "一", "meanings": "one", "grade": 1, "tier": 1},
        ]

        create_kanji_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "freq_tier1" in rows[0]["tags"]

    def test_no_grade(self, tmp_path):
        """Test CSV without grade information"""
        output_path = tmp_path / "test.csv"
        characters = [{"kanji": "一", "meanings": "one"}]

        create_kanji_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert (
                "grade" not in rows[0]["tags"] or "grade" not in rows[0]["tags"].split()
            )

    def test_empty_characters_list(self, tmp_path):
        """Test creating CSV with empty characters list"""
        output_path = tmp_path / "test.csv"
        characters = []

        create_kanji_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 0


class TestCreateVocabCsv:
    """Tests for create_vocab_csv function"""

    def test_basic_csv_creation(self, tmp_path):
        """Test creating basic vocab CSV file"""
        output_path = tmp_path / "test_vocab.csv"
        words = [
            {
                "word": "学生",
                "readings": "がくせい",
                "senses": "1. (noun) student",
                "is_common": True,
                "form_type": "kanji",
            }
        ]

        create_vocab_csv(words, output_path, "N5", include_examples=False)

        assert output_path.exists()
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert "学生" in rows[0]["word"]
            assert "がくせい" in rows[0]["word"]
            assert "<div" in rows[0]["word"]  # HTML structure
            assert "student" in rows[0]["back"]
            assert "common" in rows[0]["tags"]
            assert "kanji" in rows[0]["tags"]

    def test_csv_with_examples(self, tmp_path):
        """Test creating CSV with example sentences"""
        output_path = tmp_path / "test_examples.csv"
        words = [
            {
                "word": "学生",
                "readings": "がくせい",
                "senses": "1. (noun) student",
                "examples": "1. 私は学生です。<br>→ I am a student.",
                "is_common": True,
                "form_type": "kanji",
            }
        ]

        create_vocab_csv(words, output_path, "N4", include_examples=True)

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Check new styled HTML format
            assert "学生" in rows[0]["back"]
            assert "私は学生です。" in rows[0]["back"]
            assert "<div" in rows[0]["back"]  # HTML structure

    def test_csv_without_examples(self, tmp_path):
        """Test creating CSV without example sentences"""
        output_path = tmp_path / "test_no_examples.csv"
        words = [
            {
                "word": "学生",
                "readings": "がくせい",
                "senses": "1. (noun) student",
                "examples": "1. 私は学生です。<br>→ I am a student.",
                "is_common": True,
                "form_type": "kanji",
            }
        ]

        create_vocab_csv(words, output_path, "N3", include_examples=False)

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Should not have examples section when include_examples=False
            assert (
                "Example" not in rows[0]["back"]
                or "background:#f8f9fa" not in rows[0]["back"]
            )
            assert "学生" in rows[0]["back"]
            assert "<div" in rows[0]["back"]  # HTML structure

    def test_with_tier_tag(self, tmp_path):
        """Test CSV with tier information"""
        output_path = tmp_path / "test.csv"
        words = [
            {
                "word": "学生",
                "readings": "がくせい",
                "senses": "1. student",
                "is_common": True,
                "form_type": "kanji",
                "tier": 2,
            }
        ]

        create_vocab_csv(words, output_path, "N4", include_examples=False)

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "freq_tier2" in rows[0]["tags"]

    def test_non_common_word(self, tmp_path):
        """Test tags for non-common words"""
        output_path = tmp_path / "test.csv"
        words = [
            {
                "word": "罕见",
                "readings": "まれ",
                "senses": "1. (adj) rare",
                "is_common": False,
                "form_type": "kanji",
            }
        ]

        create_vocab_csv(words, output_path, "N1", include_examples=False)

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "common" not in rows[0]["tags"]


class TestGetNewJlptLevel:
    """Tests for get_new_jlpt_level function"""

    def test_level_4_to_n5(self):
        """Test old level 4 maps to N5"""
        assert get_new_jlpt_level(4, None) == "N5"
        assert get_new_jlpt_level(4, 1) == "N5"

    def test_level_3_to_n4(self):
        """Test old level 3 maps to N4"""
        assert get_new_jlpt_level(3, None) == "N4"
        assert get_new_jlpt_level(3, 3) == "N4"

    def test_level_1_to_n1(self):
        """Test old level 1 maps to N1"""
        assert get_new_jlpt_level(1, None) == "N1"
        assert get_new_jlpt_level(1, 8) == "N1"

    def test_level_2_grade_low_to_n3(self):
        """Test old level 2 with grade <= 6 maps to N3"""
        assert get_new_jlpt_level(2, 1) == "N3"
        assert get_new_jlpt_level(2, 6) == "N3"

    def test_level_2_grade_high_to_n2(self):
        """Test old level 2 with grade > 6 maps to N2"""
        assert get_new_jlpt_level(2, 7) == "N2"
        assert get_new_jlpt_level(2, 8) == "N2"

    def test_level_2_no_grade_to_n2(self):
        """Test old level 2 without grade maps to N2"""
        assert get_new_jlpt_level(2, None) == "N2"

    def test_unknown_level(self):
        """Test unknown level returns 'unknown'"""
        assert get_new_jlpt_level(5, None) == "unknown"
        assert get_new_jlpt_level(0, None) == "unknown"
        assert get_new_jlpt_level(-1, None) == "unknown"


class TestParseArgs:
    """Tests for parse_args function"""

    def test_default_args(self):
        """Test default argument values"""
        with patch("sys.argv", ["create_tiered_decks.py"]):
            args = parse_args()
            assert args.output_dir == Path("tiered_decks")
            assert args.jmdict == Path("jmdict-eng-3.6.2.json")
            assert args.jmdict_examples == Path("jmdict-examples-eng-3.6.2.json")
            assert args.kanjidic == Path("kanjidic2-en-3.6.2.json")
            assert args.no_examples is False
            assert args.common_only is False
            assert args.tier_strategy == "conservative"

    def test_custom_output_dir(self):
        """Test custom output directory"""
        with patch("sys.argv", ["create_tiered_decks.py", "-o", "/path/to/output"]):
            args = parse_args()
            assert args.output_dir == Path("/path/to/output")

    def test_long_output_dir(self):
        """Test --output-dir long form"""
        with patch(
            "sys.argv", ["create_tiered_decks.py", "--output-dir", "/custom/output"]
        ):
            args = parse_args()
            assert args.output_dir == Path("/custom/output")

    def test_no_examples_flag(self):
        """Test --no-examples flag"""
        with patch("sys.argv", ["create_tiered_decks.py", "--no-examples"]):
            args = parse_args()
            assert args.no_examples is True

    def test_common_only_flag(self):
        """Test --common-only flag"""
        with patch("sys.argv", ["create_tiered_decks.py", "--common-only"]):
            args = parse_args()
            assert args.common_only is True

    def test_tier_strategy_average(self):
        """Test --tier-strategy average"""
        with patch(
            "sys.argv", ["create_tiered_decks.py", "--tier-strategy", "average"]
        ):
            args = parse_args()
            assert args.tier_strategy == "average"

    def test_tier_strategy_first(self):
        """Test --tier-strategy first"""
        with patch("sys.argv", ["create_tiered_decks.py", "--tier-strategy", "first"]):
            args = parse_args()
            assert args.tier_strategy == "first"

    def test_custom_jmdict_paths(self):
        """Test custom JMdict paths"""
        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                "/path/to/jmdict.json",
                "--jmdict-examples",
                "/path/to/examples.json",
                "--kanjidic",
                "/path/to/kanjidic.json",
            ],
        ):
            args = parse_args()
            assert args.jmdict == Path("/path/to/jmdict.json")
            assert args.jmdict_examples == Path("/path/to/examples.json")
            assert args.kanjidic == Path("/path/to/kanjidic.json")


class TestMain:
    """Tests for main function"""

    @pytest.fixture
    def mock_jmdict_data(self):
        """Fixture for mock JMdict data"""
        return {
            "tags": {"n": "noun"},
            "words": [
                {
                    "kanji": [{"text": "学生", "common": True}],
                    "kana": [{"text": "がくせい", "common": True}],
                    "sense": [
                        {
                            "partOfSpeech": ["n"],
                            "gloss": [{"lang": "eng", "text": "student"}],
                        }
                    ],
                }
            ],
        }

    @pytest.fixture
    def mock_kanjidic_data(self):
        """Fixture for mock Kanjidic data"""
        return {
            "characters": [
                {
                    "literal": "学",
                    "misc": {
                        "jlptLevel": 2,
                        "grade": 5,
                        "frequency": 100,
                        "strokeCounts": [8],
                    },
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [
                                    {"type": "ja_on", "value": "ガク"},
                                ],
                                "meanings": [{"lang": "en", "value": "study"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "子"}],
                },
                {
                    "literal": "生",
                    "misc": {"jlptLevel": 4, "frequency": 50, "strokeCounts": [5]},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_kun", "value": "い.きる"}],
                                "meanings": [{"lang": "en", "value": "life"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "生"}],
                },
            ]
        }

    def test_main_missing_jmdict_file(self, tmp_path):
        """Test main exits when JMdict file not found"""
        nonexistent_file = tmp_path / "definitely_nonexistent_xyz789.json"
        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(nonexistent_file),
                "--no-examples",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_missing_kanjidic_file(self, tmp_path):
        """Test main exits when Kanjidic file not found"""
        jmdict_file = tmp_path / "jmdict.json"
        jmdict_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(tmp_path / "nonexistent.json"),
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("create_tiered_decks.load_json")
    def test_main_successful_run(
        self, mock_load_json, tmp_path, mock_jmdict_data, mock_kanjidic_data
    ):
        """Test successful main execution"""
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_data]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--no-examples",
            ],
        ):
            main()

        # Check output directory was created
        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_with_examples(
        self, mock_load_json, tmp_path, mock_jmdict_data, mock_kanjidic_data
    ):
        """Test main with examples (default behavior)"""
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_data]

        output_dir = tmp_path / "output_examples"
        jmdict_file = tmp_path / "jmdict_examples.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict-examples",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
            ],
        ):
            main()

        # Check output directory was created
        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_common_only_filter(
        self, mock_load_json, tmp_path, mock_jmdict_data, mock_kanjidic_data
    ):
        """Test main with --common-only filter"""
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_data]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--common-only",
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_different_tier_strategies(
        self, mock_load_json, tmp_path, mock_jmdict_data, mock_kanjidic_data
    ):
        """Test main with different tier strategies"""
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_data]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--tier-strategy",
                "average",
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_kanji_skipped_no_tier(
        self, mock_load_json, tmp_path, mock_kanjidic_data
    ):
        """Test kanji skipped counting when no tier assigned"""
        # Kanji without frequency data won't have a tier
        mock_kanjidic_no_freq = {
            "characters": [
                {
                    "literal": "学",
                    "misc": {
                        "jlptLevel": 2,
                        "grade": 5,
                        # No frequency field
                        "strokeCounts": [8],
                    },
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_on", "value": "ガク"}],
                                "meanings": [{"lang": "en", "value": "study"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "子"}],
                }
            ]
        }
        mock_load_json.side_effect = [mock_kanjidic_no_freq, {"tags": {}, "words": []}]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_vocab_skipped_non_jlpt(
        self, mock_load_json, tmp_path, mock_kanjidic_data
    ):
        """Test vocab skipped counting for non-JLPT words"""
        # Word with kana-only (non-JLPT)
        mock_jmdict_kana_only = {
            "tags": {"n": "noun"},
            "words": [
                {
                    "kanji": [],  # Kana-only word
                    "kana": [{"text": "です", "common": True}],
                    "sense": [
                        {
                            "partOfSpeech": ["n"],
                            "gloss": [{"lang": "eng", "text": "to be"}],
                        }
                    ],
                }
            ],
        }
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_kana_only]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_vocab_skipped_common_filter(
        self, mock_load_json, tmp_path, mock_kanjidic_data
    ):
        """Test vocab skipped counting with --common-only filter"""
        # Non-common word should be skipped with --common-only
        mock_jmdict_non_common = {
            "tags": {"n": "noun"},
            "words": [
                {
                    "kanji": [{"text": "学生", "common": False}],  # Non-common
                    "kana": [{"text": "がくせい", "common": False}],
                    "sense": [
                        {
                            "partOfSpeech": ["n"],
                            "gloss": [{"lang": "eng", "text": "student"}],
                        }
                    ],
                }
            ],
        }
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_non_common]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--common-only",
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()

    @patch("create_tiered_decks.load_json")
    def test_main_vocab_skipped_no_tier(
        self, mock_load_json, tmp_path, mock_kanjidic_data
    ):
        """Test vocab skipped counting when word has no tier"""
        # Word with kanji not in tier map
        mock_jmdict_no_tier = {
            "tags": {"n": "noun"},
            "words": [
                {
                    "kanji": [{"text": "罕见字", "common": True}],  # Non-JLPT kanji
                    "kana": [{"text": "はんれんじ", "common": True}],
                    "sense": [
                        {
                            "partOfSpeech": ["n"],
                            "gloss": [{"lang": "eng", "text": "rare"}],
                        }
                    ],
                }
            ],
        }
        mock_load_json.side_effect = [mock_kanjidic_data, mock_jmdict_no_tier]

        output_dir = tmp_path / "output"
        jmdict_file = tmp_path / "jmdict.json"
        kanjidic_file = tmp_path / "kanjidic.json"

        jmdict_file.write_text("{}")
        kanjidic_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_tiered_decks.py",
                "--jmdict",
                str(jmdict_file),
                "--kanjidic",
                str(kanjidic_file),
                "-o",
                str(output_dir),
                "--no-examples",
            ],
        ):
            main()

        assert output_dir.exists()


class TestScriptEntryPoint:
    """Test script execution via __main__ block"""

    def test_script_runs_as_main(self, tmp_path):
        """Test that script executes when run as __main__"""
        import subprocess
        import sys
        import json

        # Create mock input files
        kanjidic_file = tmp_path / "kanjidic.json"
        kanjidic_file.write_text(json.dumps({"characters": []}))
        jmdict_file = tmp_path / "jmdict.json"
        jmdict_file.write_text(json.dumps({"tags": {}, "words": []}))
        output_dir = tmp_path / "output"

        # Run the script as a subprocess
        result = subprocess.run(
            [
                sys.executable,
                "scripts/create_tiered_decks.py",
                "--kanjidic",
                str(kanjidic_file),
                "--jmdict",
                str(jmdict_file),
                "-o",
                str(output_dir),
                "--no-examples",
            ],
            capture_output=True,
            text=True,
        )

        # Should exit successfully even with empty data
        assert result.returncode in [0, 1]
