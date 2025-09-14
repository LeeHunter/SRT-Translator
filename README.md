# SRT-Translator

A Python batch processor for translating SRT subtitle files between languages, with optional vocabulary breakdown and pinyin support for Chinese.

## Features
- Batch process all `.srt` files in an `input` folder
- Translate subtitles from any source language to any target language (using Google Translate)
- Optionally include original text and vocabulary breakdown in output (this feature is for creating Anki flashcards. See my Anki-Slicer repository for more information)
- For Chinese source, the vocabulary breakdown includes pinyin
- Outputs processed files to an `output` folder
- Simple GUI for language and option selection

## Usage
1. Place your `.srt` files in a folder named `input` (case-insensitive) in the project directory (i.e. `input` is a subfolder of the location where this script is located).
2. Run the script:
   ```sh
   python3 srt_processor.py
   ```
3. Use the GUI to select source/target languages and options, then click Start.
4. Processed files will appear in the `output` folder. If that folder doesn't exist it will be created.

## Requirements
- Python 3
- Packages: `googletrans`, `jieba`, `pypinyin`
  - The script will auto-install these if missing.

## Example
- Translate Chinese SRT files to English, with vocabulary and pinyin:
  - Source: `zh-cn` or `zh-tw`
  - Target: `en`

## License
MIT
