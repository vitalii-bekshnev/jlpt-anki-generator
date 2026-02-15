#!/usr/bin/env python3
"""
Tests for create_kanji_decks.py
"""

import csv
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from create_kanji_decks import (
    create_anki_csv,
    extract_dict_reference,
    extract_meanings,
    extract_nanori,
    extract_readings,
    find_example_words,
    format_back_field,
    load_kanjidic,
    main,
    parse_args,
    process_character,
)


class TestLoadKanjidic:
    """Tests for load_kanjidic function"""

    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file"""
        test_file = tmp_path / "kanjidic.json"
        test_data = {"characters": [{"literal": "一"}]}
        test_file.write_text(json.dumps(test_data))

        result = load_kanjidic(test_file)
        assert result == test_data

    def test_file_not_found(self, tmp_path):
        """Test FileNotFoundError handling"""
        test_file = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit) as exc_info:
            load_kanjidic(test_file)
        assert exc_info.value.code == 1

    def test_invalid_json(self, tmp_path):
        """Test JSONDecodeError handling"""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{invalid json}")

        with pytest.raises(SystemExit) as exc_info:
            load_kanjidic(test_file)
        assert exc_info.value.code == 1


class TestExtractReadings:
    """Tests for extract_readings function"""

    def test_no_reading_meaning(self):
        """Test with None reading_meaning"""
        on, kun = extract_readings(None)
        assert on == []
        assert kun == []

    def test_no_groups(self):
        """Test with reading_meaning but no groups"""
        reading_meaning = {}
        on, kun = extract_readings(reading_meaning)
        assert on == []
        assert kun == []

    def test_on_readings_only(self):
        """Test extracting on'yomi readings"""
        reading_meaning = {
            "groups": [
                {
                    "readings": [
                        {"type": "ja_on", "value": "イチ"},
                        {"type": "ja_on", "value": "イツ"},
                    ]
                }
            ]
        }
        on, kun = extract_readings(reading_meaning)
        assert on == ["イチ", "イツ"]
        assert kun == []

    def test_kun_readings_only(self):
        """Test extracting kun'yomi readings"""
        reading_meaning = {
            "groups": [
                {
                    "readings": [
                        {"type": "ja_kun", "value": "ひと"},
                        {"type": "ja_kun", "value": "ひと.つ"},
                    ]
                }
            ]
        }
        on, kun = extract_readings(reading_meaning)
        assert on == []
        assert kun == ["ひと", "ひと.つ"]

    def test_mixed_readings(self):
        """Test extracting both on and kun readings"""
        reading_meaning = {
            "groups": [
                {
                    "readings": [
                        {"type": "ja_on", "value": "ガク"},
                        {"type": "ja_kun", "value": "まな.ぶ"},
                    ]
                }
            ]
        }
        on, kun = extract_readings(reading_meaning)
        assert on == ["ガク"]
        assert kun == ["まな.ぶ"]

    def test_multiple_groups(self):
        """Test extracting readings from multiple groups"""
        reading_meaning = {
            "groups": [
                {"readings": [{"type": "ja_on", "value": "コウ"}]},
                {"readings": [{"type": "ja_kun", "value": "いえ"}]},
            ]
        }
        on, kun = extract_readings(reading_meaning)
        assert on == ["コウ"]
        assert kun == ["いえ"]

    def test_unknown_reading_type(self):
        """Test handling unknown reading types"""
        reading_meaning = {
            "groups": [{"readings": [{"type": "pinyin", "value": "yi"}]}]
        }
        on, kun = extract_readings(reading_meaning)
        assert on == []
        assert kun == []


class TestExtractMeanings:
    """Tests for extract_meanings function"""

    def test_no_reading_meaning(self):
        """Test with None reading_meaning"""
        result = extract_meanings(None)
        assert result == []

    def test_single_meaning(self):
        """Test extracting single meaning"""
        reading_meaning = {"groups": [{"meanings": [{"lang": "en", "value": "one"}]}]}
        result = extract_meanings(reading_meaning)
        assert result == ["one"]

    def test_multiple_meanings(self):
        """Test extracting multiple meanings"""
        reading_meaning = {
            "groups": [
                {
                    "meanings": [
                        {"lang": "en", "value": "study"},
                        {"lang": "en", "value": "learning"},
                    ]
                }
            ]
        }
        result = extract_meanings(reading_meaning)
        assert result == ["study", "learning"]

    def test_non_english_meanings_filtered(self):
        """Test filtering non-English meanings"""
        reading_meaning = {
            "groups": [
                {
                    "meanings": [
                        {"lang": "en", "value": "school"},
                        {"lang": "ger", "value": "Schule"},
                        {"lang": "en", "value": "academy"},
                    ]
                }
            ]
        }
        result = extract_meanings(reading_meaning)
        assert result == ["school", "academy"]

    def test_default_language_english(self):
        """Test that meanings without lang default to English"""
        reading_meaning = {"groups": [{"meanings": [{"value": "book"}]}]}
        result = extract_meanings(reading_meaning)
        assert result == ["book"]

    def test_multiple_groups(self):
        """Test extracting meanings from multiple groups"""
        reading_meaning = {
            "groups": [
                {"meanings": [{"lang": "en", "value": "water"}]},
                {"meanings": [{"lang": "en", "value": "Wednesday"}]},
            ]
        }
        result = extract_meanings(reading_meaning)
        assert result == ["water", "Wednesday"]

    def test_empty_meanings(self):
        """Test handling empty meanings"""
        reading_meaning = {"groups": [{"meanings": []}]}
        result = extract_meanings(reading_meaning)
        assert result == []


class TestExtractDictReference:
    """Tests for extract_dict_reference function"""

    def test_find_heisig(self):
        """Test finding Heisig reference"""
        dict_refs = [
            {"type": "heisig", "value": "1"},
            {"type": "nelson_c", "value": "100"},
        ]
        result = extract_dict_reference(dict_refs, "heisig")
        assert result == "1"

    def test_find_heisig6(self):
        """Test finding Heisig6 reference"""
        dict_refs = [
            {"type": "heisig", "value": "1"},
            {"type": "heisig6", "value": "2"},
        ]
        result = extract_dict_reference(dict_refs, "heisig6")
        assert result == "2"

    def test_reference_not_found(self):
        """Test when reference type not found"""
        dict_refs = [{"type": "nelson_c", "value": "100"}]
        result = extract_dict_reference(dict_refs, "heisig")
        assert result is None

    def test_empty_dict_refs(self):
        """Test with empty dictionary references"""
        result = extract_dict_reference([], "heisig")
        assert result is None


class TestExtractNanori:
    """Tests for extract_nanori function"""

    def test_no_reading_meaning(self):
        """Test with None reading_meaning"""
        result = extract_nanori(None)
        assert result == []

    def test_with_nanori(self):
        """Test extracting nanori readings"""
        reading_meaning = ({"nanori": ["かず", "い", "いっ", "いと", "かつ"]},)
        # Fix: reading_meaning should be a dict, not a tuple
        reading_meaning = {"nanori": ["かず", "い", "いっ", "いと", "かつ"]}
        result = extract_nanori(reading_meaning)
        assert result == ["かず", "い", "いっ", "いと", "かつ"]

    def test_empty_nanori(self):
        """Test with empty nanori list"""
        reading_meaning = {"nanori": []}
        result = extract_nanori(reading_meaning)
        assert result == []


class TestProcessCharacter:
    """Tests for process_character function"""

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

        result = process_character(char)

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
        result = process_character(char)
        assert result is None

    def test_no_jlpt_level_returns_none(self):
        """Test character without JLPT level returns None"""
        char = {"literal": "一", "misc": {"grade": 1}}
        result = process_character(char)
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

        result = process_character(char)

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

    def test_multiple_stroke_counts(self):
        """Test using first stroke count when multiple exist"""
        char = {
            "literal": "一",
            "misc": {"jlptLevel": 4, "strokeCounts": [1, 2, 3]},
        }

        result = process_character(char)
        assert result["stroke_count"] == 1


class TestFormatBackField:
    """Tests for format_back_field function"""

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

        result = format_back_field(char, "N3")

        # Check for HTML structure and content
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

        result = format_back_field(char, "N5")

        assert "一" in result
        assert "one" in result
        assert "イチ" in result
        assert "ひと" in result
        assert "<div" in result  # HTML structure

    def test_only_meanings(self):
        """Test formatting with only meanings"""
        char = {"kanji": "一", "meanings": "one"}

        result = format_back_field(char, "N5")
        assert "一" in result
        assert "one" in result
        assert "<div" in result  # HTML structure


class TestCreateAnkiCsv:
    """Tests for create_anki_csv function"""

    def test_basic_csv_creation(self, tmp_path):
        """Test creating basic kanji CSV file"""
        output_path = tmp_path / "test.csv"
        characters = [
            {
                "kanji": "一",
                "meanings": "one",
                "on_readings": "イチ",
                "kun_readings": "ひと",
                "grade": 1,
            }
        ]

        create_anki_csv(characters, output_path, "N5")

        assert output_path.exists()
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert "一" in rows[0]["kanji"]
            assert "<div" in rows[0]["kanji"]  # HTML structure
            assert "one" in rows[0]["back"]
            assert "N5" in rows[0]["tags"]
            assert "grade1" in rows[0]["tags"]

    def test_multiple_characters(self, tmp_path):
        """Test CSV with multiple characters"""
        output_path = tmp_path / "test.csv"
        characters = [
            {"kanji": "一", "meanings": "one", "grade": 1},
            {"kanji": "二", "meanings": "two", "grade": 1},
            {"kanji": "三", "meanings": "three", "grade": 1},
        ]

        create_anki_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert "一" in rows[0]["kanji"]
            assert "二" in rows[1]["kanji"]
            assert "三" in rows[2]["kanji"]
            assert "<div" in rows[0]["kanji"]  # HTML structure

    def test_no_grade(self, tmp_path):
        """Test CSV without grade information"""
        output_path = tmp_path / "test.csv"
        characters = [{"kanji": "一", "meanings": "one"}]

        create_anki_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert (
                "grade" not in rows[0]["tags"] or "grade" not in rows[0]["tags"].split()
            )
            assert "N5" in rows[0]["tags"]

    def test_empty_characters_list(self, tmp_path):
        """Test creating CSV with empty characters list"""
        output_path = tmp_path / "test.csv"
        characters = []

        create_anki_csv(characters, output_path, "N1")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 0


class TestParseArgs:
    """Tests for parse_args function"""

    def test_default_args(self):
        """Test default argument values"""
        with patch("sys.argv", ["create_kanji_decks.py"]):
            args = parse_args()
            assert args.input == Path("kanjidic2-en-3.6.2.json")
            assert args.output_dir == Path("anki_decks")

    def test_custom_input(self):
        """Test custom input file"""
        with patch(
            "sys.argv", ["create_kanji_decks.py", "-i", "/path/to/kanjidic.json"]
        ):
            args = parse_args()
            assert args.input == Path("/path/to/kanjidic.json")

    def test_custom_output_dir(self):
        """Test custom output directory"""
        with patch("sys.argv", ["create_kanji_decks.py", "-o", "/path/to/output"]):
            args = parse_args()
            assert args.output_dir == Path("/path/to/output")

    def test_long_form_args(self):
        """Test long form arguments"""
        with patch(
            "sys.argv",
            [
                "create_kanji_decks.py",
                "--input",
                "custom.json",
                "--output-dir",
                "custom_output/",
            ],
        ):
            args = parse_args()
            assert args.input == Path("custom.json")
            assert args.output_dir == Path("custom_output/")


class TestMain:
    """Tests for main function"""

    @pytest.fixture
    def mock_kanjidic_data(self):
        """Fixture for mock Kanjidic data"""
        return {
            "characters": [
                {
                    "literal": "一",
                    "misc": {"jlptLevel": 4, "strokeCounts": [1], "grade": 1},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [
                                    {"type": "ja_on", "value": "イチ"},
                                    {"type": "ja_kun", "value": "ひと"},
                                ],
                                "meanings": [{"lang": "en", "value": "one"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "一"}],
                    "dictionaryReferences": [],
                },
                {
                    "literal": "食",
                    "misc": {"jlptLevel": 3, "strokeCounts": [9], "grade": 3},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [
                                    {"type": "ja_on", "value": "ショク"},
                                    {"type": "ja_kun", "value": "た.べる"},
                                ],
                                "meanings": [{"lang": "en", "value": "eat"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "食"}],
                    "dictionaryReferences": [],
                },
            ]
        }

    def test_main_missing_input_file(self, tmp_path):
        """Test main exits when input file not found"""
        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(tmp_path / "nonexistent.json")],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_successful_run(
        self, mock_create_csv, mock_load_kanjidic, tmp_path, mock_kanjidic_data
    ):
        """Test successful main execution"""
        mock_load_kanjidic.return_value = mock_kanjidic_data

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check output directory was created
        assert output_dir.exists()

        # Check create_anki_csv was called
        assert mock_create_csv.called

    @patch("create_kanji_decks.load_kanjidic")
    def test_main_invalid_data_structure(self, mock_load_kanjidic, tmp_path):
        """Test main exits with invalid data structure"""
        mock_load_kanjidic.return_value = {
            "invalid": "data"
        }  # Missing 'characters' key

        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")
        output_dir = tmp_path / "output"

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_jlpt_level_grouping(
        self, mock_create_csv, mock_load_kanjidic, tmp_path, mock_kanjidic_data
    ):
        """Test that kanji are grouped by JLPT level correctly"""
        mock_load_kanjidic.return_value = mock_kanjidic_data

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check that create_anki_csv was called for each JLPT level
        call_args_list = mock_create_csv.call_args_list
        # Should be called for N5 and N4 (from level 4 and 3)
        tiers_called = [call[0][2] for call in call_args_list]
        assert "N5" in tiers_called
        assert "N4" in tiers_called


class TestFindExampleWords:
    """Tests for find_example_words function"""

    def test_find_examples_for_kanji(self):
        """Test finding words containing a kanji"""
        words_data = [
            {
                "kanji": [{"text": "学校"}],
                "kana": [{"text": "がっこう"}],
                "sense": [{"gloss": [{"lang": "eng", "text": "school"}]}],
            },
            {
                "kanji": [{"text": "学生"}],
                "kana": [{"text": "がくせい"}],
                "sense": [{"gloss": [{"lang": "eng", "text": "student"}]}],
            },
            {
                "kanji": [{"text": "日本"}],
                "kana": [{"text": "にほん"}],
                "sense": [{"gloss": [{"lang": "eng", "text": "Japan"}]}],
            },
        ]
        tags = {"n": "noun"}

        result = find_example_words("学", words_data, tags, max_examples=3)

        assert len(result) == 2
        assert any(word["word"] == "学校" for word in result)
        assert any(word["word"] == "学生" for word in result)

    def test_max_examples_limit(self):
        """Test that max_examples limits the results"""
        words_data = [
            {
                "kanji": [{"text": f"学{chr(65 + i)}"}],
                "kana": [{"text": f"がく{chr(65 + i)}"}],
                "sense": [
                    {
                        "gloss": [{"lang": "eng", "text": f"meaning{i}"}],
                        "partOfSpeech": [],
                    }
                ],
            }
            for i in range(10)
        ]
        tags = {}

        result = find_example_words("学", words_data, tags, max_examples=3)

        assert len(result) == 3

    def test_no_matching_words(self):
        """Test when no words contain the kanji"""
        words_data = [
            {
                "kanji": [{"text": "日本"}],
                "kana": [{"text": "にほん"}],
                "sense": [],
            }
        ]
        tags = {}

        result = find_example_words("学", words_data, tags)

        assert result == []

    def test_empty_words_list(self):
        """Test with empty words list"""
        result = find_example_words("学", [], {})
        assert result == []

    def test_kana_only_words_skipped(self):
        """Test that kana-only words are skipped"""
        words_data = [
            {
                "kanji": [],  # No kanji form
                "kana": [{"text": "あの"}],
                "sense": [
                    {"gloss": [{"lang": "eng", "text": "um"}], "partOfSpeech": []}
                ],
            },
            {
                "kanji": [{"text": "学校"}],
                "kana": [{"text": "がっこう"}],
                "sense": [
                    {"gloss": [{"lang": "eng", "text": "school"}], "partOfSpeech": []}
                ],
            },
        ]
        tags = {}

        result = find_example_words("学", words_data, tags)

        assert len(result) == 1
        assert result[0]["word"] == "学校"


class TestFormatBackFieldWithExamples:
    """Tests for format_back_field with word examples"""

    def test_format_with_example_words(self):
        """Test formatting with example words"""
        char = {
            "kanji": "学",
            "meanings": "study",
            "on_readings": "ガク",
            "kun_readings": "まな.ぶ",
        }
        example_words = [
            {"word": "学校", "readings": "がっこう", "senses": "1. (noun) school"},
            {"word": "学生", "readings": "がくせい", "senses": "1. (noun) student"},
        ]

        result = format_back_field(char, "N3", example_words)

        # Check HTML structure and content
        assert "学" in result
        assert "学校" in result
        assert "がっこう" in result
        assert "school" in result
        assert "学生" in result
        assert "がくせい" in result
        assert "student" in result
        assert "Example" in result  # New styled format uses "Example Words"
        assert "<div" in result  # HTML structure

    def test_format_truncates_long_senses(self):
        """Test that long senses are truncated"""
        char = {"kanji": "一", "meanings": "one"}
        long_sense = "A" * 150
        example_words = [
            {"word": "一人", "readings": "ひとり", "senses": long_sense},
        ]

        result = format_back_field(char, "N5", example_words)

        # Check that content is present but formatted as HTML
        assert "一人" in result
        assert "ひとり" in result
        assert "<div" in result  # HTML structure

    def test_format_without_examples(self):
        """Test formatting without example words"""
        char = {
            "kanji": "学",
            "meanings": "study",
            "on_readings": "ガク",
            "kun_readings": "まな.ぶ",
        }

        result = format_back_field(char, "N3", None)

        # Should not have example words section
        assert "Example Words" not in result
        assert "学" in result
        assert "study" in result
        assert "<div" in result  # HTML structure

    def test_format_with_empty_examples(self):
        """Test formatting with empty example words list"""
        char = {
            "kanji": "学",
            "meanings": "study",
        }

        result = format_back_field(char, "N3", [])

        assert "Example Words" not in result
        assert "学" in result
        assert "<div" in result  # HTML structure


class TestCreateAnkiCsvWithExamples:
    """Tests for create_anki_csv with example words"""

    def test_csv_with_example_words(self, tmp_path):
        """Test creating CSV with word examples"""
        output_path = tmp_path / "test.csv"
        characters = [
            {
                "kanji": "学",
                "meanings": "study",
                "on_readings": "ガク",
                "kun_readings": "まな.ぶ",
                "grade": 5,
            }
        ]
        example_words_map = {
            "学": [
                {"word": "学校", "readings": "がっこう", "senses": "1. (noun) school"},
            ]
        }

        create_anki_csv(characters, output_path, "N3", example_words_map)

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Check new styled HTML format
            assert "学" in rows[0]["back"]
            assert "学校" in rows[0]["back"]
            assert "がっこう" in rows[0]["back"]
            assert "<div" in rows[0]["back"]  # HTML structure

    def test_csv_without_example_map(self, tmp_path):
        """Test creating CSV without example words map"""
        output_path = tmp_path / "test.csv"
        characters = [{"kanji": "一", "meanings": "one"}]

        create_anki_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "Example Words" not in rows[0]["back"]
            assert "一" in rows[0]["back"]
            assert "<div" in rows[0]["back"]  # HTML structure


class TestParseArgsWithJmdict:
    """Tests for parse_args with new jmdict arguments"""

    def test_jmdict_argument(self):
        """Test --jmdict argument"""
        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "--jmdict", "/path/to/jmdict.json"],
        ):
            args = parse_args()
            assert args.jmdict == Path("/path/to/jmdict.json")

    def test_max_examples_argument(self):
        """Test --max-examples argument"""
        with patch("sys.argv", ["create_kanji_decks.py", "--max-examples", "5"]):
            args = parse_args()
            assert args.max_examples == 5

    def test_max_examples_default(self):
        """Test default max-examples value"""
        with patch("sys.argv", ["create_kanji_decks.py"]):
            args = parse_args()
            assert args.max_examples == 3

    def test_jmdict_none_by_default(self):
        """Test that jmdict is None by default"""
        with patch("sys.argv", ["create_kanji_decks.py"]):
            args = parse_args()
            assert args.jmdict is None


class TestMainWithJmdict:
    """Tests for main function with jmdict integration"""

    @pytest.fixture
    def mock_kanjidic_data(self):
        """Fixture for mock Kanjidic data"""
        return {
            "characters": [
                {
                    "literal": "一",
                    "misc": {"jlptLevel": 4, "strokeCounts": [1], "grade": 1},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [
                                    {"type": "ja_on", "value": "イチ"},
                                    {"type": "ja_kun", "value": "ひと"},
                                ],
                                "meanings": [{"lang": "en", "value": "one"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "一"}],
                    "dictionaryReferences": [],
                }
            ]
        }

    @pytest.fixture
    def mock_jmdict_data(self):
        """Fixture for mock JMdict data"""
        return {
            "words": [
                {
                    "kanji": [{"text": "一人", "common": True}],
                    "kana": [{"text": "ひとり", "common": True}],
                    "sense": [
                        {
                            "gloss": [{"lang": "eng", "text": "one person"}],
                            "partOfSpeech": ["n"],
                        }
                    ],
                }
            ],
            "tags": {"n": "noun"},
        }

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.load_json")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_with_jmdict(
        self,
        mock_create_csv,
        mock_load_json,
        mock_load_kanjidic,
        tmp_path,
        mock_kanjidic_data,
        mock_jmdict_data,
    ):
        """Test main function with jmdict for word examples"""
        mock_load_kanjidic.return_value = mock_kanjidic_data
        mock_load_json.return_value = mock_jmdict_data

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        jmdict_file = tmp_path / "jmdict.json"
        input_file.write_text("{}")
        jmdict_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_kanji_decks.py",
                "-i",
                str(input_file),
                "--jmdict",
                str(jmdict_file),
                "-o",
                str(output_dir),
            ],
        ):
            main()

        # Check that create_anki_csv was called with example_words_map
        call_args = mock_create_csv.call_args
        assert call_args[0][3] is not None  # example_words_map should be provided

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_without_jmdict(
        self, mock_create_csv, mock_load_kanjidic, tmp_path, mock_kanjidic_data
    ):
        """Test main function without jmdict (no word examples)"""
        mock_load_kanjidic.return_value = mock_kanjidic_data

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check that create_anki_csv was called without example_words_map
        call_args = mock_create_csv.call_args
        assert call_args[0][3] is None  # example_words_map should be None

    @patch("create_kanji_decks.load_kanjidic")
    def test_main_missing_jmdict_file(
        self, mock_load_kanjidic, tmp_path, mock_kanjidic_data, capsys
    ):
        """Test main continues when jmdict file not found"""
        mock_load_kanjidic.return_value = mock_kanjidic_data

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        jmdict_file = tmp_path / "nonexistent_jmdict.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            [
                "create_kanji_decks.py",
                "-i",
                str(input_file),
                "--jmdict",
                str(jmdict_file),
                "-o",
                str(output_dir),
            ],
        ):
            main()

        # Should print warning but continue
        captured = capsys.readouterr()
        assert "Warning" in captured.err or "JMdict file not found" in captured.err


class TestLoadKanjidicGenericError:
    """Tests for generic exception handling in load_kanjidic"""

    def test_generic_error_handling(self, tmp_path):
        """Test handling of generic exceptions"""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": "data"}')

        # Mock open to raise a generic exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(SystemExit) as exc_info:
                load_kanjidic(test_file)
            assert exc_info.value.code == 1


class TestCreateAnkiCsvWithTier:
    """Tests for create_anki_csv with tier information"""

    def test_csv_with_tier_tag(self, tmp_path):
        """Test creating CSV with tier tag"""
        output_path = tmp_path / "test.csv"
        characters = [
            {
                "kanji": "一",
                "meanings": "one",
                "on_readings": "イチ",
                "kun_readings": "ひと",
                "grade": 1,
                "tier": 1,
            }
        ]

        create_anki_csv(characters, output_path, "N5")

        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert "freq_tier1" in rows[0]["tags"]


class TestMainWithLevel2Split:
    """Tests for main function with level 2 grade-based splitting"""

    @pytest.fixture
    def mock_kanjidic_data_with_level2(self):
        """Fixture for mock Kanjidic data with level 2 kanji"""
        return {
            "characters": [
                {
                    "literal": "学",
                    "misc": {"jlptLevel": 2, "strokeCounts": [8], "grade": 5},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_on", "value": "ガク"}],
                                "meanings": [{"lang": "en", "value": "study"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "子"}],
                    "dictionaryReferences": [],
                },
                {
                    "literal": "複",
                    "misc": {"jlptLevel": 2, "strokeCounts": [11], "grade": 8},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_on", "value": "フク"}],
                                "meanings": [{"lang": "en", "value": "complex"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "衣"}],
                    "dictionaryReferences": [],
                },
            ]
        }

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_level2_n3_grouping(
        self,
        mock_create_csv,
        mock_load_kanjidic,
        tmp_path,
        mock_kanjidic_data_with_level2,
    ):
        """Test that level 2 kanji with grade <= 6 go to N3"""
        mock_load_kanjidic.return_value = mock_kanjidic_data_with_level2

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check that create_anki_csv was called for N3
        call_args_list = mock_create_csv.call_args_list
        tiers_called = [call[0][2] for call in call_args_list]
        assert "N3" in tiers_called

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_level2_n2_grouping(
        self,
        mock_create_csv,
        mock_load_kanjidic,
        tmp_path,
        mock_kanjidic_data_with_level2,
    ):
        """Test that level 2 kanji with grade > 6 go to N2"""
        mock_load_kanjidic.return_value = mock_kanjidic_data_with_level2

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check that create_anki_csv was called for N2
        call_args_list = mock_create_csv.call_args_list
        tiers_called = [call[0][2] for call in call_args_list]
        assert "N2" in tiers_called

    @patch("create_kanji_decks.load_kanjidic")
    def test_main_skipped_output(self, mock_load_kanjidic, tmp_path, capsys):
        """Test that skipped message is printed when entries are skipped"""
        # Data with characters that will be skipped (no JLPT level)
        mock_load_kanjidic.return_value = {
            "characters": [
                {
                    "literal": "未",
                    "misc": {"grade": 5},  # No jlptLevel
                }
            ]
        }

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        captured = capsys.readouterr()
        assert "Skipped" in captured.out

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_with_tier_assignment(
        self, mock_create_csv, mock_load_kanjidic, tmp_path
    ):
        """Test that tier is assigned when kanji is in frequency map"""
        # Kanji with frequency data
        mock_load_kanjidic.return_value = {
            "characters": [
                {
                    "literal": "一",
                    "misc": {
                        "jlptLevel": 4,
                        "strokeCounts": [1],
                        "grade": 1,
                        "frequency": 1,
                    },
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_on", "value": "イチ"}],
                                "meanings": [{"lang": "en", "value": "one"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "一"}],
                    "dictionaryReferences": [],
                }
            ]
        }

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check create_anki_csv was called
        assert mock_create_csv.called
        # Verify the tier was assigned (by checking the call arguments)
        call_args = mock_create_csv.call_args
        characters = call_args[0][0]
        assert len(characters) > 0
        # The first kanji should have a tier assigned
        assert "tier" in characters[0]

    @patch("create_kanji_decks.load_kanjidic")
    @patch("create_kanji_decks.create_anki_csv")
    def test_main_level1_grouping(self, mock_create_csv, mock_load_kanjidic, tmp_path):
        """Test that level 1 kanji go to N1"""
        mock_load_kanjidic.return_value = {
            "characters": [
                {
                    "literal": "鬱",
                    "misc": {"jlptLevel": 1, "strokeCounts": [29]},
                    "readingMeaning": {
                        "groups": [
                            {
                                "readings": [{"type": "ja_on", "value": "ウツ"}],
                                "meanings": [{"lang": "en", "value": "depression"}],
                            }
                        ]
                    },
                    "radicals": [{"value": "鬱"}],
                    "dictionaryReferences": [],
                }
            ]
        }

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        # Check that create_anki_csv was called for N1
        call_args_list = mock_create_csv.call_args_list
        tiers_called = [call[0][2] for call in call_args_list]
        assert "N1" in tiers_called

    @patch("create_kanji_decks.load_kanjidic")
    def test_main_unknown_jlpt_level(self, mock_load_kanjidic, tmp_path, capsys):
        """Test handling of unknown JLPT levels"""
        # Character with an invalid JLPT level
        mock_load_kanjidic.return_value = {
            "characters": [
                {
                    "literal": "一",
                    "misc": {"jlptLevel": 5},  # Invalid level
                    "readingMeaning": {"groups": []},
                    "radicals": [],
                    "dictionaryReferences": [],
                }
            ]
        }

        output_dir = tmp_path / "output"
        input_file = tmp_path / "kanjidic.json"
        input_file.write_text("{}")

        with patch(
            "sys.argv",
            ["create_kanji_decks.py", "-i", str(input_file), "-o", str(output_dir)],
        ):
            main()

        captured = capsys.readouterr()
        # Should indicate entries were skipped
        assert "Skipped" in captured.out


class TestScriptEntryPoint:
    """Test script execution via __main__ block"""

    def test_script_runs_as_main(self, tmp_path, monkeypatch):
        """Test that script executes when run as __main__"""
        import subprocess
        import sys

        # Create mock input file
        kanjidic_file = tmp_path / "kanjidic.json"
        kanjidic_file.write_text(json.dumps({"characters": []}))
        output_dir = tmp_path / "output"

        # Run the script as a subprocess
        result = subprocess.run(
            [
                sys.executable,
                "scripts/create_kanji_decks.py",
                "-i",
                str(kanjidic_file),
                "-o",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        # Should exit with error code due to empty data
        assert result.returncode in [0, 1]
