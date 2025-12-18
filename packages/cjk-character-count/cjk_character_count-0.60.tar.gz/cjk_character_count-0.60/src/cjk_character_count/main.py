import argparse
import sys
from pathlib import Path
from .FontInfoCollector import FontInfoCollector
from .global_var import DisplayLanguage, CJKGroup, DisplayCJKTablesList, DisplayUnicodeBlocksList
from .localise import get_localised_label
import pandas as pd

def get_report_data(cjk_char_count, unicode_char_count, lang=DisplayLanguage.EN):
    # Keys localization
    keys = {
        DisplayLanguage.EN: ("Charset", "Count", "Total", "Group"),
        DisplayLanguage.ZHS: ("字符集", "支持数", "总数", "分组"),
        DisplayLanguage.ZHT: ("字符集", "計數", "總數", "分組"),
    }
    k_name, k_count, k_total, k_group = keys.get(lang, keys[DisplayLanguage.EN])

    data = []

    # CJK Sections
    section_order = [CJKGroup.FAN, CJKGroup.JIANFAN, CJKGroup.JIAN]
    if lang == DisplayLanguage.ZHS:
        section_order = [CJKGroup.JIAN, CJKGroup.JIANFAN, CJKGroup.FAN]

    for section_label in section_order:
        group_name = get_localised_label(lang, 'section_titles')[section_label]
        tables = DisplayCJKTablesList.get_ordered_tables_in_group(section_label)
        for enc_key, enc_info in tables.items():
            count = cjk_char_count.get(enc_key, 0)
            total = enc_info.count
            name = enc_info.localised_name(lang)
            data.append({
                k_name: name,
                k_count: count,
                k_total: total,
                k_group: group_name
            })

    # Unicode Sections
    group_name = get_localised_label(lang, 'section_titles.uni')
    blocks = DisplayUnicodeBlocksList.get_ordered_blocks()
    for uni_block_id, uni_block in blocks.items():
        count = unicode_char_count.get(uni_block_id, 0)
        total = len(uni_block.assigned_ranges)
        name = get_localised_label(lang, "unicode_blocks").get(uni_block.name, uni_block.name)
        data.append({
            k_name: name,
            k_count: count,
            k_total: total,
            k_group: group_name
        })
    
    return data, k_name


def character(file_path, lang="zhs", format="df", font_id=-1):
    """
    Library entry point to count CJK characters in a font.
    
    Args:
        file_path (str | Path): Path to the font file.
        lang (str): Language code ('en', 'zhs', 'zht'). Default is 'zhs'.
        format (str): Output format ('txt', 'df'). Default is 'df'.
        font_id (int): Font ID for TTC files. Default is -1 (auto/first).
        
    Returns:
        str | pandas.DataFrame: The report in the requested format.
    """
    filename = Path(file_path).resolve()
    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    # Determine language enum
    lang_map = {
        "en": DisplayLanguage.EN,
        "zhs": DisplayLanguage.ZHS,
        "zht": DisplayLanguage.ZHT
    }
    lang_enum = lang_map.get(lang, DisplayLanguage.ZHS)

    # Callback for TTC handling - for library usage, we default to 0 if not specified
    # or raise error if ambiguity cannot be resolved without interaction?
    # For simplicity in library mode, if font_id is -1, we pick 0 but warn?
    # Or better, we just use font_id.
    def ttc_selector(font_list):
        if font_id != -1:
            return font_id
        # Default to first font if not specified in library mode
        return 0

    font = FontInfoCollector.load_font(filename, ttc_selector)
    cjk_count, uni_count = font.count_cjk_chars()

    if format == "df":
        data, k_name = get_report_data(cjk_count, uni_count, lang_enum)
        df = pd.DataFrame(data)
        df.set_index(k_name, inplace=True)
        return df
    else:
        # Generate text report
        output = []
        output.append(f"File: {font.font_path.name}")
        output.append(f"Font: {font.font_name}")
        output.append("-" * 30)
        
        # Determine section order based on language
        section_order = [CJKGroup.FAN, CJKGroup.JIANFAN, CJKGroup.JIAN]
        if lang_enum == DisplayLanguage.ZHS:
            section_order = [CJKGroup.JIAN, CJKGroup.JIANFAN, CJKGroup.FAN]

        # Print CJK sections
        for section_label in section_order:
            output.append(f"=== {get_localised_label(lang_enum, 'section_titles')[section_label]} ===")
            
            tables = DisplayCJKTablesList.get_ordered_tables_in_group(section_label)
            for enc_key, enc_info in tables.items():
                count = cjk_count.get(enc_key, 0)
                total = enc_info.count
                name = enc_info.localised_name(lang_enum)
                output.append(f"{name}: {count}/{total}")
            output.append("")

        # Print Unicode sections
        output.append(f"=== {get_localised_label(lang_enum, 'section_titles.uni')} ===")
        
        blocks = DisplayUnicodeBlocksList.get_ordered_blocks()
        for uni_block_id, uni_block in blocks.items():
            count = uni_count.get(uni_block_id, 0)
            total = len(uni_block.assigned_ranges)
            name = get_localised_label(lang_enum, "unicode_blocks").get(uni_block.name, uni_block.name)
            output.append(f"{name}: {count}/{total}")
            
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        prog="CJK Character Count",
        description="A CLI tool to count CJK characters in a font file."
    )
    parser.add_argument("filename", help="Path to the font file")
    parser.add_argument("--font-id", type=int, default=-1, help="Font ID for TTC files (default: auto/0)")
    parser.add_argument("--lang", choices=["en", "zhs", "zht"], default="zhs", help="Output language (default: zhs)")
    parser.add_argument("--format", choices=["txt", "df"], default="df", help="Output format: txt or df (default)")

    args = parser.parse_args()
    
    try:
        result = character(args.filename, args.lang, args.format, args.font_id)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
