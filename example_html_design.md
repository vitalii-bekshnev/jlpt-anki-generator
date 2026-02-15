# Anki CSV HTML Design Examples

This document demonstrates custom HTML designs for JLPT Anki deck CSVs.

## Current Basic Format

The current CSV uses basic HTML:

```csv
word,back,tags
雨,"<b>Reading:</b> あめ<br><b>Meanings:</b> rain",common
```

## Proposed Enhanced Design

### 1. Vocabulary Card with Modern Styling

```csv
word,back,tags
雨,"<div style='font-family: Noto Sans JP,sans-serif;max-width:600px;margin:0 auto'>
<div style='background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:20px;border-radius:12px 12px 0 0;text-align:center'>
<div style='font-size:48px;font-weight:bold;text-shadow:2px 2px 4px rgba(0,0,0,0.3)'>雨</div>
<div style='font-size:24px;letter-spacing:2px'>あめ</div>
</div>
<div style='background:#fafafa;padding:20px;border-radius:0 0 12px 12px;box-shadow:0 4px 6px rgba(0,0,0,0.1)'>
<div style='color:#667eea;font-weight:bold;font-size:14px;text-transform:uppercase;border-bottom:2px solid #667eea;padding-bottom:4px;margin-bottom:12px'>Meanings</div>
<div>1. rain<br>2. rainy day</div>
<div style='background:#fff;padding:15px;border-radius:8px;border-left:4px solid #764ba2;margin-top:15px'>
<div style='font-size:18px;color:#333'>雨のために...</div>
<div style='font-size:14px;color:#666;font-style:italic'>Because of the rain...</div>
</div>
</div>
</div>",n5 common
```

### 2. Kanji Card Design

```csv
kanji,back,tags
雨,"<div style='font-family:Noto Sans JP,sans-serif;max-width:600px;margin:0 auto'>
<div style='background:linear-gradient(135deg,#11998e,#38ef7d);color:#fff;padding:25px;border-radius:12px 12px 0 0;text-align:center'>
<div style='font-size:64px;font-weight:bold;text-shadow:3px 3px 6px rgba(0,0,0,0.3)'>雨</div>
<div style='font-size:20px'>rain</div>
</div>
<div style='background:#fafafa;padding:20px'>
<div style='display:flex;gap:15px;margin-bottom:20px'>
<div style='flex:1;background:#fff;padding:15px;border-radius:8px;border-top:3px solid #11998e'>
<div style='color:#11998e;font-size:12px;font-weight:bold;text-transform:uppercase'>On'yomi</div>
<div style='font-size:18px'>ウ</div>
</div>
<div style='flex:1;background:#fff;padding:15px;border-radius:8px;border-top:3px solid #38ef7d'>
<div style='color:#38ef7d;font-size:12px;font-weight:bold;text-transform:uppercase'>Kun'yomi</div>
<div style='font-size:18px'>あめ</div>
</div>
</div>
<div style='background:#fff;padding:15px;border-radius:8px'>
<div style='color:#666;font-size:14px;font-weight:bold;text-transform:uppercase;margin-bottom:12px'>Stats</div>
<div style='display:flex;justify-content:space-around;text-align:center'>
<div><div style='font-size:24px;font-weight:bold;color:#11998e'>8</div><div style='font-size:11px;color:#999'>Strokes</div></div>
<div><div style='font-size:24px;font-weight:bold;color:#11998e'>#950</div><div style='font-size:11px;color:#999'>Freq</div></div>
</div>
</div>
</div>
</div>",grade1
```

### 3. Compact Mobile Design

```csv
word,back,tags
雨,"<div style='font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif'>
<div style='background:#4a90e2;color:#fff;padding:12px 16px'>
<div style='font-size:32px;font-weight:bold'>雨</div>
<div style='font-size:16px'>あめ</div>
</div>
<div style='background:#fff;padding:16px'>
<div style='color:#4a90e2;font-size:12px;font-weight:600;text-transform:uppercase'>Meaning</div>
<div style='color:#333;font-size:16px'>rain</div>
<div style='background:#f8f9fa;padding:12px;border-radius:6px;border-left:3px solid #4a90e2;margin-top:12px'>
<div style='color:#666;font-size:13px'>雨が降る</div>
<div style='color:#888;font-size:12px;font-style:italic'>It's raining</div>
</div>
</div>
</div>",n5
```

## Design Principles

1. **Inline CSS Only**: Works within Anki constraints
2. **Mobile Responsive**: Adapts to different screen sizes
3. **Color Coding**: N5=blue, N4=green, N3=orange, N2=red, N1=purple
4. **Visual Hierarchy**: Clear word/reading/meanings/sections
5. **No External Dependencies**: All self-contained

## Usage

CSV values with HTML must be wrapped in double quotes. Newlines within fields are preserved within quoted strings.
