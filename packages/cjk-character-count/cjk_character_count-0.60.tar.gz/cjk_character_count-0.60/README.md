# CJK-character-count

This is a program that counts the amount of CJK characters based on Unicode ranges and Chinese encoding standards.  
此软件以统一码（Unicode）区块与汉字编码标准统计字体内的汉字数量。

---

## 来源

This program is adapted from [NightFurySL2001/CJK-character-count](https://github.com/NightFurySL2001/CJK-character-count), and has been modified into CLI and API versions with added output formats (txt or pandas DataFrame).

本程序来源于 [NightFurySL2001/CJK-character-count](https://github.com/NightFurySL2001/CJK-character-count)，修改为 cli 和 api 版本，并添加了输出格式（txt 或 pandas DataFrame）。

## How this works 如何运作

This program accepts 1 font file at a time (OpenType/TrueType single font file currently) and extract the character list from `cmap` table, which records the Unicode (base-10)-glyph shape for a font. The list is then parsed to count the amount of characters based on Unicode ranges (comparing the hexadecimal range) and Chinese encoding standards (given a list of .txt files with the actual character in it).  
此软件可计算一套字体内的汉字数量，目前只限 OpenType/TrueType 单字体文件而已。导入字体时，软件将从`cmap`表（储存字体内（十进制）统一码与字符对应的表）提取汉字列表，然后以该列表依统一码区块（比对十六进制码位）与汉字编码标准（比对 .txt 文件）统计字体内的汉字数量。

## Currently supported font formats 支援的字体格式

Major font formats are supported in this software.  
主要字体格式本软件皆都支援。

` *.ttf, *.otf, *.woff, *.woff2, *.ttc, *.otc`

## Installation 安装

This project uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.
本项目使用 [uv](https://docs.astral.sh/uv) 进行依赖管理，请确保已安装：

```bash
uv sync
```

## Usage 使用方法

### CLI (Command Line Interface) 命令行

Basic usage:
基础用法：

```sh
python main.py /path/to/font.ttf
```

**Options 选项:**

*   `filename`: Path to the font file. (Required)
    *   字体文件路径。（必填）
*   `--font-id`: Font ID for TTC/OTC files (default: -1, auto-select first).
    *   TTC/OTC 字体 ID（默认：-1，自动选择第一个）。
*   `--lang`: Output language / 输出语言 (`en`, `zhs`, `zht`, default: `zhs`).
*   `--format`: Output format / 输出格式 (`txt`, `df`, default: `df`).
    *   `txt`: Plain text report. 纯文本报告。
    *   `df`: Pandas DataFrame string representation. Pandas DataFrame 字符串表示。

**Examples 示例:**

```sh
# Default (Simplified Chinese, DataFrame output)
# 默认（简体中文，DataFrame 输出）
uv run main myfont.ttf

# Traditional Chinese, Text output
# 繁体中文，文本输出
uv run main myfont.ttf --lang zht --format txt

# Specific font in a TTC collection
# 指定 TTC 集合中的特定字体
uv run main myfont.ttc --font-id 1
```

### Library (Python Import) 库引用

You can use this tool as a library in your own Python scripts.
您可以在自己的 Python 脚本中将此工具作为库引用。

```python
from cjk_character_count import character

# Get text report (default language is zhs, default format is df)
# 获取报告（默认语言为 zhs，默认格式为 df）
df = character("path/to/font.ttf")
print(df)

# Get DataFrame with Traditional Chinese headers
# 获取繁体中文表头的 DataFrame
df_zht = character("path/to/font.ttf", lang="zht", format="df")
print(df_zht)

# Get text report
# 获取文本报告
text_report = character("path/to/font.ttf", format="txt")
print(text_report)
```

## Currently supported encoding standard/standardization list 支援的编码标准／汉字表

Details of the character lists can be found in https://github.com/NightFurySL2001/cjktables.  
字表详情可参见 https://github.com/NightFurySL2001/cjktables 。

### Encoding standard 编码标准

-   [GB/T 2312](https://en.wikipedia.org/wiki/GB_2312)

-   [GB/T 12345](https://zh.wikipedia.org/wiki/GB_12345)  
    \*_Note: Source file from [character_set](https://gitlab.com/mrhso/character_set/-/blob/master/GB12345.txt) by @mrhso.  
    注：字表来源为 @mrhso [character_set](https://gitlab.com/mrhso/character_set/-/blob/master/GB12345.txt)。_

-   [GBK](<https://en.wikipedia.org/wiki/GBK_(character_encoding)>)  
    \*_Note: Private Use Area (PUA) characters are removed and not counted, resulting in 20923 characters.  
    注：不计算私用区（PUA）字符，共计 20923 字。_

-   [GB 18030-2022 Implementation Level 1/实现等级 1](https://en.wikipedia.org/wiki/GB_18030)

-   [GB/Z 40637-2021 Standard Glyph List of Generally Used Chinese Chars for Ancient Books Publishing/古籍印刷通用字规范字形表](https://zh.wikipedia.org/zh-my/%E5%8F%A4%E7%B1%8D%E5%8D%B0%E5%88%B7%E9%80%9A%E7%94%A8%E5%AD%97%E8%A7%84%E8%8C%83%E5%AD%97%E5%BD%A2%E8%A1%A8)

-   [BIG5/五大码](https://en.wikipedia.org/wiki/Big5)

-   [BIG 5 Common Character Set/五大码常用汉字表](https://en.wikipedia.org/wiki/Big5)

-   [Hong Kong Supplementary Character Set (HKSCS)/香港增补字符集](https://en.wikipedia.org/wiki/Hong_Kong_Supplementary_Character_Set)

-   [IICore/国际表意文字核心](https://appsrv.cse.cuhk.edu.hk/~irg/irg/IICore/IICore.htm)（Deprecated/已废除）

-   [Hong Kong Supplementary Character Set/香港增補字符集](https://zh.wikipedia.org/wiki/%E9%A6%99%E6%B8%AF%E5%A2%9E%E8%A3%9C%E5%AD%97%E7%AC%A6%E9%9B%86)

-   [jf7000 Core Set/当务字集基本包](https://justfont.com/jf7000)

### Standardization list 汉字表

-   [List of Frequently Used Characters in Modern Chinese/现代汉语常用字表](https://zh.wiktionary.org/wiki/Appendix:%E7%8E%B0%E4%BB%A3%E6%B1%89%E8%AF%AD%E5%B8%B8%E7%94%A8%E5%AD%97%E8%A1%A8)  
    \*_Note: Old name in this software was 3500 Commonly Used Chinese Characters.  
    注：旧版软件内名称为《3500 字常用汉字表》。_

-   [List of Commonly Used Characters in Modern Chinese/现代汉语通用字表](https://zh.wiktionary.org/wiki/Appendix:%E7%8E%B0%E4%BB%A3%E6%B1%89%E8%AF%AD%E9%80%9A%E7%94%A8%E5%AD%97%E8%A1%A8)

-   [Table of General Standard Chinese Characters/通用规范汉字表](https://en.wikipedia.org/wiki/Table_of_General_Standard_Chinese_Characters)

-   [List of Frequently Used Characters of Compulsory Education/义务教育语文课程常用字表](https://old.pep.com.cn/xiaoyu/jiaoshi/tbjx/kbjd/kb2011/201202/t20120206_1099050.htm)

-   [Chart of Standard Forms of Common National Characters/常用國字標準字體表](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%9C%8B%E5%AD%97%E6%A8%99%E6%BA%96%E5%AD%97%E9%AB%94%E8%A1%A8)  
    \*_Note: Old name in this software was 《台湾教育部常用字表》。  
    注：旧版软件内名称为《台湾教育部常用字表》。_
-   [Chart of Standard Forms of Less-Than-Common National Characters/次常用國字標準字體表](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%9C%8B%E5%AD%97%E6%A8%99%E6%BA%96%E5%AD%97%E9%AB%94%E8%A1%A8)  
    \*_Note: Old name in this software was 《台湾教育部次常用字表》, and was temporarily removed in v0.10 and v0.11.  
    注：旧版软件内名称为《台湾教育部次常用字表》，并于 0.10 版和 0.11 版暂时移除。_

-   [List of Graphemes of Commonly-used Chinese Characters (Online version)/常用字字形表（线上版）](https://zh.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E5%AD%97%E5%AD%97%E5%BD%A2%E8%A1%A8)

-   [Supplementary Character Set (suppchara, level 1-6)/常用香港外字表（1-6 级）](https://github.com/ichitenfont/suppchara)

### Foundry list 厂商字表

-   [Hanyi Fonts Simp./Trad. List/汉仪简繁字表](https://github.com/3type/glyphs-han/blob/master/Tables/Commonly%20Used%20on%20Internet.txt)

-   FounderType Simp./Trad. List 方正简繁字表

## License 授权

This software is licensed under [MIT License](https://opensource.org/licenses/MIT). Details of the license can be found in the [accompanying `LICENSE` file](LICENSE).  
本软件以 [MIT 授权条款](https://opensource.org/licenses/MIT)发布。授权详情可在[随附的 `LICENSE` 文件内](LICENSE)查阅。

## Changelog 更新日志

Refer to [readme.txt](readme.txt). 参考[readme.txt](readme.txt)。

---

This program is requested by [ziticool](ztcool.com.cn). Visit their site to see this in action.

此软件由[ziticool](ztcool.com.cn)要求。浏览该网址以查看使用方式。

## 致谢

Thank you to [NightFurySL2001](https://github.com/NightFurySL2001) for the original code.
The complete refactoring was done by [Trae](https://www.trae.ai/) .
The translation was completed by [DeepSeek](https://www.deepseek.com/) .

感谢 [NightFurySL2001](https://github.com/NightFurySL2001) 提供的原始代码。
重构由 [Trae](https://www.trae.ai/)  完成。
翻译由 [DeepSeek](https://www.deepseek.com/) 完成。