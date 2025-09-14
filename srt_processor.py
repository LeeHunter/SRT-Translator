import tkinter as tk
from tkinter import filedialog, messagebox

# List of valid ISO 639-1 codes (partial, can be extended)
VALID_LANG_CODES = {
    "en",
    "zh-cn",
    "zh-tw",
    "fr",
    "de",
    "es",
    "it",
    "ja",
    "ko",
    "ru",
    "pt",
    "ar",
    "hi",
    "tr",
    "vi",
    "th",
    "id",
    "nl",
    "pl",
    "sv",
    "fi",
    "no",
    "da",
    "cs",
    "el",
    "he",
    "ro",
    "hu",
    "sk",
    "uk",
    "bg",
    "hr",
    "lt",
    "lv",
    "et",
    "sl",
    "sr",
    "ms",
    "ca",
    "fa",
    "ur",
    "bn",
    "ta",
    "te",
    "ml",
    "gu",
    "kn",
    "pa",
    "mr",
    "sw",
    "zu",
    "af",
    "eu",
    "gl",
    "is",
    "mt",
    "sq",
    "mk",
    "az",
    "hy",
    "ka",
    "be",
    "uz",
    "kk",
    "ky",
    "mn",
    "lo",
    "km",
    "my",
    "si",
    "ne",
    "ps",
    "sd",
    "am",
    "om",
    "so",
    "ti",
    "yi",
    "yo",
    "xh",
    "zu",
}


def show_options_dialog():
    root = tk.Tk()
    root.title("SRT Batch Processor Options")
    root.geometry("350x220")
    root.resizable(False, False)

    tk.Label(root, text="Enter source file language (e.g. zh-cn)").pack(pady=(10, 0))
    src_lang_var = tk.StringVar(value="zh-cn")
    src_entry = tk.Entry(root, textvariable=src_lang_var)
    src_entry.pack(pady=(0, 10))

    tk.Label(root, text="Enter target language (e.g. en)").pack()
    tgt_lang_var = tk.StringVar(value="en")
    tgt_entry = tk.Entry(root, textvariable=tgt_lang_var)
    tgt_entry.pack(pady=(0, 10))

    add_source_var = tk.BooleanVar(value=True)
    vocab_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Add source to output", variable=add_source_var).pack(anchor="w", padx=20)
    tk.Checkbutton(root, text="Generate vocabulary list", variable=vocab_var).pack(anchor="w", padx=20)

    options = {}
    def start():
        src = src_lang_var.get().strip().lower()
        tgt = tgt_lang_var.get().strip().lower()
        if src not in VALID_LANG_CODES:
            messagebox.showerror("Invalid Source Language", f"Source language code '{src}' is not valid.")
            return
        if tgt not in VALID_LANG_CODES:
            messagebox.showerror("Invalid Target Language", f"Target language code '{tgt}' is not valid.")
            return
        options["src_lang"] = src
        options["tgt_lang"] = tgt
        options["add_source"] = add_source_var.get()
        options["vocab"] = vocab_var.get()
        root.destroy()
    tk.Button(root, text="Start", command=start).pack(pady=(15, 0))
    root.mainloop()
    return options if options else None


#!/usr/bin/env python3
"""
SRT Subtitle Processor
Processes all SRT files in 'input' folder and moves results to 'output' folder.
"""

import re
import os
import sys
import shutil
import glob
import time
from googletrans import Translator
import jieba
from pypinyin import lazy_pinyin, Style


def install_requirements():
    """Install required packages if not available."""
    try:
        import googletrans
        import jieba
        import pypinyin
    except ImportError:
        print("Installing required packages...")
        os.system("pip install googletrans==4.0.0rc1 jieba pypinyin")
        print("Packages installed. Please run the script again.")
        sys.exit(1)


def parse_srt_file(filepath):
    """Parse SRT file and return list of subtitle entries."""
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # Split by double newlines to separate subtitle blocks
    blocks = re.split(r"\n\s*\n", content.strip())
    subtitles = []

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            subtitle_num = lines[0]
            timestamp = lines[1]
            text = "\n".join(lines[2:])
            subtitles.append(
                {"number": subtitle_num, "timestamp": timestamp, "text": text}
            )

    return subtitles


def get_pinyin(word):
    """Get pinyin for a Chinese word."""
    try:
        # Use TONE instead of TONE_MARKS for compatibility
        pinyin_list = lazy_pinyin(word, style=Style.TONE)
        return "".join(pinyin_list)
    except AttributeError:
        # Fallback if Style.TONE doesn't work
        pinyin_list = lazy_pinyin(word)
        return "".join(pinyin_list)


def translate_text(text, translator, src_lang, tgt_lang):
    """Translate text from src_lang to tgt_lang with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            clean_text = text.strip().replace("\n", " ")
            if not clean_text:
                return "[No text to translate]"
            result = translator.translate(clean_text, src=src_lang, dest=tgt_lang)
            if result and result.text:
                return result.text
            else:
                return "[Translation failed - no result]"
        except Exception as e:
            print(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                translator = Translator()
            else:
                return "[Translation failed after retries]"
    return "[Translation failed]"


def get_vocabulary_breakdown(text, translator, src_lang, tgt_lang):
    """Get vocabulary breakdown for text, optionally with pinyin if Chinese."""
    # Segment the text into words
    words = jieba.cut(text)
    unique_words = []
    seen = set()

    for word in words:
        word = word.strip()
        # Only include Chinese characters, avoid single characters and duplicates
        if (
            word
            and len(word) >= 1
            and re.search(r"[\u4e00-\u9fff]", word)
            and word not in seen
            and not re.match(r'^[，。！？；：""\'\'（）【】\s]+$', word)
        ):  # Skip pure punctuation
            seen.add(word)
            unique_words.append(word)

    vocabulary = []
    for word in unique_words:
        try:
            translation = translate_text(word, translator, src_lang=src_lang, tgt_lang=tgt_lang)
            if src_lang in ["zh-cn", "zh-tw"]:
                pinyin = get_pinyin(word)
                vocabulary.append(f"- {word}     {pinyin}     {translation}")
            else:
                vocabulary.append(f"- {word}     {translation}")
        except Exception as e:
            print(f"Error processing word '{word}': {e}")
            continue
    if vocabulary:
        return [""] + vocabulary
    else:
        return []


def process_srt_file(input_filepath, output_dir, src_lang, tgt_lang, add_source, vocab):
    """Process a single SRT file and create enhanced version in output directory."""
    translator = Translator()
    subtitles = parse_srt_file(input_filepath)
    filename = os.path.basename(input_filepath)
    name, ext = os.path.splitext(filename)
    output_filepath = os.path.join(output_dir, f"{tgt_lang.upper()}_{name}{ext}")
    print(f"Processing {filename} with {len(subtitles)} subtitle entries...")
    enhanced_subtitles = []
    for i, subtitle in enumerate(subtitles):
        if (i + 1) % 5 == 0:
            print(f"  Processing subtitle {i+1}/{len(subtitles)}")
        original_text = subtitle["text"]
        # Always translate
        translation = translate_text(original_text, translator, src_lang, tgt_lang)
        # Build enhanced text
        enhanced_text = ""
        if add_source:
            enhanced_text += original_text + "\n"
        enhanced_text += translation
        if vocab:
            vocab_list = get_vocabulary_breakdown(original_text, translator, src_lang, tgt_lang)
            if vocab_list:
                enhanced_text += "\n" + "\n".join(vocab_list)
        enhanced_subtitle = {
            "number": subtitle["number"],
            "timestamp": subtitle["timestamp"],
            "text": enhanced_text,
        }
        enhanced_subtitles.append(enhanced_subtitle)
        time.sleep(0.1)
    with open(output_filepath, "w", encoding="utf-8") as file:
        for i, subtitle in enumerate(enhanced_subtitles):
            file.write(f"{subtitle['number']}\n")
            file.write(f"{subtitle['timestamp']}\n")
            file.write(f"{subtitle['text']}\n")
            if i < len(enhanced_subtitles) - 1:
                file.write("\n")
    print(f"  Enhanced file created: {tgt_lang.upper()}_{name}{ext}")
    return output_filepath


def main():
    install_requirements()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Find input folder (case-insensitive)
    input_dir = None
    for name in os.listdir(script_dir):
        if name.lower() == "input" and os.path.isdir(os.path.join(script_dir, name)):
            input_dir = os.path.join(script_dir, name)
            break
    output_dir = os.path.join(script_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output folder: {output_dir}")
    options = show_options_dialog()
    if not options:
        print("No options selected. Exiting.")
        return
    if not input_dir:
        print("No input folder or no SRT files in folder.")
        messagebox.showerror("Error", "No input folder or no SRT files in folder.")
        return
    srt_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".srt")]
    if not srt_files:
        print("No input folder or no SRT files in folder.")
        messagebox.showerror("Error", "No input folder or no SRT files in folder.")
        return
    print(f"Found {len(srt_files)} SRT file(s) to process:")
    for srt_file in srt_files:
        print(f"  - {srt_file}")
    processed_files = []
    for srt_file in srt_files:
        input_path = os.path.join(input_dir, srt_file)
        try:
            enhanced_file = process_srt_file(
                input_path,
                output_dir,
                options["src_lang"],
                options["tgt_lang"],
                options["add_source"],
                options["vocab"],
            )
            processed_files.append((input_path, enhanced_file))
            print(f"✓ Successfully processed {srt_file}\n")
        except Exception as e:
            print(f"✗ Error processing {srt_file}: {e}\n")
    # Move originals and outputs to output folder
    print("Moving original and output files to output folder...")
    for original_file, enhanced_file in processed_files:
        try:
            shutil.move(original_file, output_dir)
            shutil.move(enhanced_file, output_dir)
            print(f"  Moved {os.path.basename(original_file)} and {os.path.basename(enhanced_file)}")
        except Exception as e:
            print(f"  Error moving files: {e}")
    print("\nProcessing complete!")


if __name__ == "__main__":
    main()
