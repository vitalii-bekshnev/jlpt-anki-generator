#!/usr/bin/env python3
"""
HTML card templates for JLPT Anki decks.

Provides styled HTML generation for vocabulary and kanji cards.
"""

from typing import List, Optional, Dict


def get_jlpt_colors(jlpt_level: str) -> Dict[str, str]:
    """Get color scheme for a JLPT level."""
    colors = {
        "N5": {
            "primary": "#4a90e2",
            "secondary": "#357abd",
            "gradient": "#4a90e2,#5ba3f5",
        },
        "N4": {
            "primary": "#11998e",
            "secondary": "#0d7a6e",
            "gradient": "#11998e,#38ef7d",
        },
        "N3": {
            "primary": "#f5a623",
            "secondary": "#d68910",
            "gradient": "#f5a623,#f7b84e",
        },
        "N2": {
            "primary": "#e74c3c",
            "secondary": "#c0392b",
            "gradient": "#e74c3c,#ec7063",
        },
        "N1": {
            "primary": "#9b59b6",
            "secondary": "#8e44ad",
            "gradient": "#9b59b6,#af7ac5",
        },
        "kana": {
            "primary": "#34495e",
            "secondary": "#2c3e50",
            "gradient": "#34495e,#5d6d7e",
        },
        "non_jlpt": {
            "primary": "#7f8c8d",
            "secondary": "#616a6b",
            "gradient": "#7f8c8d,#99a3a4",
        },
    }
    return colors.get(jlpt_level, colors["N5"])


def create_vocab_front(word: str, readings: str, jlpt_level: str = "N5") -> str:
    """
    Create a styled HTML front field for vocabulary cards.

    Args:
        word: The Japanese word/kanji
        readings: Comma-separated readings
        jlpt_level: JLPT level (N5-N1, kana, non_jlpt)

    Returns:
        HTML string for the card front
    """
    colors = get_jlpt_colors(jlpt_level)
    primary = colors["primary"]

    html = f"""<div style='font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans JP",sans-serif;max-width:500px;margin:0 auto'>
  <div style='background:{primary};color:#fff;padding:24px;border-radius:12px;text-align:center;box-shadow:0 4px 8px rgba(0,0,0,0.15)'>
    <div style='font-size:42px;font-weight:bold;margin-bottom:8px;text-shadow:2px 2px 4px rgba(0,0,0,0.2)'>{word}</div>
    <div style='font-size:20px;opacity:0.95;letter-spacing:2px'>{readings}</div>
  </div>
</div>"""

    return html


def create_kanji_front(kanji: str, jlpt_level: str = "N5") -> str:
    """
    Create a styled HTML front field for kanji cards.

    Args:
        kanji: The kanji character
        jlpt_level: JLPT level

    Returns:
        HTML string for the card front
    """
    colors = get_jlpt_colors(jlpt_level)
    primary = colors["primary"]

    html = f"""<div style='font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans JP",sans-serif;max-width:500px;margin:0 auto'>
  <div style='background:{primary};color:#fff;padding:30px;border-radius:12px;text-align:center;box-shadow:0 4px 8px rgba(0,0,0,0.15)'>
    <div style='font-size:72px;font-weight:bold;text-shadow:3px 3px 6px rgba(0,0,0,0.25);background:rgba(255,255,255,0.15);width:100px;height:100px;line-height:100px;border-radius:50%;margin:0 auto'>{kanji}</div>
  </div>
</div>"""

    return html


def format_meanings_html(meanings: str) -> str:
    """Format meanings text into styled HTML list."""
    if not meanings:
        return ""

    lines = meanings.split("<br>")
    items = []
    for line in lines:
        line = line.strip()
        if line:
            # Remove leading numbers if present
            if line[0].isdigit() and ". " in line[:3]:
                line = line.split(". ", 1)[1]
            items.append(
                f"<div style='padding:6px 0;border-bottom:1px solid #eee;color:#333'>{line}</div>"
            )

    if items:
        items[-1] = items[-1].replace("border-bottom:1px solid #eee", "")

    return "".join(items)


def format_examples_html(examples: str) -> str:
    """Format examples text into styled HTML."""
    if not examples:
        return ""

    lines = examples.split("<br>")
    formatted = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("→"):
            # This is Japanese text
            formatted.append(
                f"<div style='font-size:16px;color:#333;margin-bottom:6px'>{line}</div>"
            )
        elif line.startswith("→"):
            # This is English translation
            formatted.append(
                f"<div style='font-size:13px;color:#666;font-style:italic'>{line}</div>"
            )

    return "".join(formatted)


def create_vocab_card(
    word: str,
    readings: str,
    meanings: str,
    examples: Optional[str] = None,
    jlpt_level: str = "N5",
    is_common: bool = False,
    tier: Optional[int] = None,
) -> str:
    """
    Create a styled HTML vocabulary card.

    Args:
        word: The Japanese word/kanji
        readings: Comma-separated readings
        meanings: HTML-formatted meanings
        examples: Optional HTML-formatted examples
        jlpt_level: JLPT level (N5-N1, kana, non_jlpt)
        is_common: Whether the word is marked as common
        tier: Frequency tier (1-4)

    Returns:
        HTML string for the card back
    """
    colors = get_jlpt_colors(jlpt_level)
    primary = colors["primary"]

    # Build tags HTML
    tags_html = []
    tags_html.append(
        f"<span style='display:inline-block;background:#e3f2fd;color:{primary};padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>{jlpt_level}</span>"
    )
    if is_common:
        tags_html.append(
            "<span style='display:inline-block;background:#f3e5f5;color:#7b1fa2;padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>Common</span>"
        )
    if tier:
        tier_colors = ["#4caf50", "#8bc34a", "#ffc107", "#ff9800"]
        tier_color = tier_colors[tier - 1] if tier <= 4 else tier_colors[3]
        tags_html.append(
            f"<span style='display:inline-block;background:{tier_color}20;color:{tier_color};padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>Tier {tier}</span>"
        )

    # Build meanings HTML
    meanings_html = format_meanings_html(meanings)

    # Build examples HTML if present
    examples_section = ""
    if examples:
        examples_content = format_examples_html(examples)
        if examples_content:
            examples_section = f"""
            <div style='background:#f8f9fa;padding:12px;border-radius:6px;border-left:3px solid {primary};margin-top:12px'>
                <div style='color:{primary};font-size:11px;font-weight:600;text-transform:uppercase;margin-bottom:8px'>Example</div>
                {examples_content}
            </div>
            """

    html = f"""<div style='font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans JP",sans-serif;max-width:500px;margin:0 auto'>
  <div style='background:{primary};color:#fff;padding:16px;border-radius:8px 8px 0 0;text-align:center'>
    <div style='font-size:36px;font-weight:bold;margin-bottom:4px;text-shadow:1px 1px 2px rgba(0,0,0,0.2)'>{word}</div>
    <div style='font-size:18px;opacity:0.95;letter-spacing:1px'>{readings}</div>
  </div>
  <div style='background:#fff;padding:16px;border-radius:0 0 8px 8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)'>
    <div style='color:{primary};font-size:11px;font-weight:600;text-transform:uppercase;border-bottom:2px solid {primary};padding-bottom:4px;margin-bottom:10px'>Meanings</div>
    <div style='font-size:14px;color:#333;line-height:1.5'>
      {meanings_html}
    </div>
    {examples_section}
    <div style='margin-top:12px;text-align:center'>
      {"".join(tags_html)}
    </div>
  </div>
</div>"""

    return html


def create_kanji_card(
    kanji: str,
    meanings: str,
    on_readings: str,
    kun_readings: str,
    stroke_count: Optional[int] = None,
    radical: Optional[str] = None,
    frequency: Optional[int] = None,
    grade: Optional[int] = None,
    heisig_rtk: Optional[str] = None,
    heisig6_rtk: Optional[str] = None,
    nanori: Optional[str] = None,
    example_words: Optional[List[Dict]] = None,
    jlpt_level: str = "N5",
    tier: Optional[int] = None,
) -> str:
    """
    Create a styled HTML kanji card.

    Args:
        kanji: The kanji character
        meanings: Semicolon-separated meanings
        on_readings: Semicolon-separated on'yomi readings
        kun_readings: Semicolon-separated kun'yomi readings
        stroke_count: Number of strokes
        radical: The radical character
        frequency: Frequency rank
        grade: School grade level
        heisig_rtk: Heisig Remembering the Kanji number
        heisig6_rtk: Heisig RTK 6th edition number
        nanori: Name readings
        example_words: List of example word dictionaries
        jlpt_level: JLPT level
        tier: Frequency tier

    Returns:
        HTML string for the card back
    """
    colors = get_jlpt_colors(jlpt_level)
    primary = colors["primary"]
    secondary = colors["secondary"]

    # Build readings sections
    readings_html = ""
    if on_readings or kun_readings:
        on_section = ""
        kun_section = ""

        if on_readings:
            on_section = f"""
            <div style='flex:1;background:#f8f9fa;padding:12px;border-radius:6px;border-top:3px solid {primary}'>
              <div style='color:{primary};font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:4px'>On'yomi</div>
              <div style='font-size:16px;color:#333'>{on_readings}</div>
            </div>
            """

        if kun_readings:
            kun_section = f"""
            <div style='flex:1;background:#f8f9fa;padding:12px;border-radius:6px;border-top:3px solid {secondary}'>
              <div style='color:{secondary};font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:4px'>Kun'yomi</div>
              <div style='font-size:16px;color:#333'>{kun_readings}</div>
            </div>
            """

        readings_html = f"<div style='display:flex;gap:10px;margin-bottom:12px'>{on_section}{kun_section}</div>"

    # Build stats section
    stats_items = []
    if stroke_count:
        stats_items.append(
            f"<div style='text-align:center'><div style='font-size:20px;font-weight:bold;color:{primary}'>{stroke_count}</div><div style='font-size:10px;color:#999'>Strokes</div></div>"
        )
    if radical:
        stats_items.append(
            f"<div style='text-align:center'><div style='font-size:18px;font-weight:bold;color:{primary}'>{radical}</div><div style='font-size:10px;color:#999'>Radical</div></div>"
        )
    if frequency:
        stats_items.append(
            f"<div style='text-align:center'><div style='font-size:16px;font-weight:bold;color:{primary}'>#{frequency}</div><div style='font-size:10px;color:#999'>Freq</div></div>"
        )

    stats_html = ""
    if stats_items:
        stats_html = f"""
        <div style='background:#f8f9fa;padding:12px;border-radius:6px;margin-bottom:12px'>
          <div style='color:#666;font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:8px'>Stats</div>
          <div style='display:flex;justify-content:space-around'>
            {"".join(stats_items)}
          </div>
        </div>
        """

    # Build Heisig section
    heisig_html = ""
    if heisig_rtk or heisig6_rtk:
        heisig_parts = []
        if heisig_rtk:
            heisig_parts.append(f"<span>RTK: <strong>#{heisig_rtk}</strong></span>")
        if heisig6_rtk:
            heisig_parts.append(f"<span>RTK6: <strong>#{heisig6_rtk}</strong></span>")
        if grade:
            heisig_parts.append(f"<span>Grade: <strong>{grade}</strong></span>")

        heisig_html = f"""
        <div style='background:linear-gradient(135deg,#f5f7fa 0%,#e4e8ec 100%);padding:12px;border-radius:6px;border-left:3px solid {primary};margin-bottom:12px'>
          <div style='color:{primary};font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:6px'>References</div>
          <div style='display:flex;justify-content:space-around;font-size:13px;color:#555'>
            {" | ".join(heisig_parts)}
          </div>
        </div>
        """

    # Build nanori section
    nanori_html = ""
    if nanori:
        nanori_html = f"""
        <div style='background:#fff3e0;padding:10px;border-radius:6px;margin-bottom:12px'>
          <div style='color:#e65100;font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:4px'>Name Readings</div>
          <div style='font-size:14px;color:#333'>{nanori}</div>
        </div>
        """

    # Build example words section
    examples_html = ""
    if example_words:
        word_items = []
        for i, word in enumerate(example_words[:3], 1):  # Limit to 3 examples
            word_text = word.get("word", "")
            word_reading = word.get("readings", "")
            word_sense = word.get("senses", "")
            if len(word_sense) > 80:
                word_sense = word_sense[:80] + "..."

            word_items.append(
                f"<div style='padding:6px 0;border-bottom:1px solid #eee;font-size:13px;color:#333'><strong>{word_text}</strong> <span style='color:#666'>({word_reading})</span> - <span style='color:#333'>{word_sense}</span></div>"
            )

        if word_items:
            word_items[-1] = word_items[-1].replace("border-bottom:1px solid #eee", "")
            examples_html = f"""
            <div style='background:#f8f9fa;padding:12px;border-radius:6px'>
              <div style='color:{primary};font-size:10px;font-weight:600;text-transform:uppercase;margin-bottom:8px'>Example Words</div>
              {"".join(word_items)}
            </div>
            """

    # Build tags
    tags_html = []
    tags_html.append(
        f"<span style='display:inline-block;background:#e3f2fd;color:{primary};padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>{jlpt_level}</span>"
    )
    if tier:
        tier_colors = ["#4caf50", "#8bc34a", "#ffc107", "#ff9800"]
        tier_color = tier_colors[tier - 1] if tier <= 4 else tier_colors[3]
        tags_html.append(
            f"<span style='display:inline-block;background:{tier_color}20;color:{tier_color};padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>Tier {tier}</span>"
        )
    if grade:
        tags_html.append(
            f"<span style='display:inline-block;background:#e8f5e9;color:#388e3c;padding:4px 10px;border-radius:12px;font-size:11px;margin:2px'>Grade {grade}</span>"
        )

    html = f"""<div style='font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans JP",sans-serif;max-width:500px;margin:0 auto'>
  <div style='background:{primary};color:#fff;padding:20px;border-radius:8px 8px 0 0;text-align:center'>
    <div style='font-size:56px;font-weight:bold;margin-bottom:8px;text-shadow:2px 2px 4px rgba(0,0,0,0.2);background:rgba(255,255,255,0.15);width:90px;height:90px;line-height:90px;border-radius:50%;margin:0 auto 12px'>{kanji}</div>
    <div style='font-size:16px;opacity:0.95'>{meanings}</div>
  </div>
  <div style='background:#fff;padding:16px;border-radius:0 0 8px 8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)'>
    {readings_html}
    {stats_html}
    {nanori_html}
    {heisig_html}
    {examples_html}
    <div style='margin-top:12px;text-align:center'>
      {"".join(tags_html)}
    </div>
  </div>
</div>"""

    return html
