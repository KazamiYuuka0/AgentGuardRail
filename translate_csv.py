import csv
import argostranslate.translate

# ---- 配置 ----
INPUT_CSV = "prompts_all.csv"     # 输入 CSV 文件路径
OUTPUT_CSV = "prompts_all_zh.csv" # 输出 CSV 文件路径
SRC_COLUMN = 1                    # 要翻译的列索引（B列 = 1）
SRC_LANG = "en"
TGT_LANG = "zh"

# ---- 获取翻译引擎 ----
translation = argostranslate.translate.get_translation_from_codes(SRC_LANG, TGT_LANG)

# ---- 读取 CSV ----
with open(INPUT_CSV, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

print(f"共读取 {len(rows)} 条数据，开始翻译...\n")

# ---- 翻译并写入 ----
with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header + ["translated_zh"])

    for i, row in enumerate(rows, 1):
        original = row[SRC_COLUMN].strip() if len(row) > SRC_COLUMN else ""
        if original:
            translated = translation.translate(original)
        else:
            original = ""
            translated = ""

        writer.writerow(row + [translated])
        print(f"[{i}/{len(rows)}] {original[:40]}... => {translated[:40]}...")

print(f"\n翻译完成，结果已保存至 {OUTPUT_CSV}")
