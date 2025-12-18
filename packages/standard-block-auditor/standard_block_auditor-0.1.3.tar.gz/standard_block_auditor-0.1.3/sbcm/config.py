"""
標準ブロック比較法：共通設定ファイル (Configuration)
全ての計算ツール・分析ツールはこのファイルの定数を参照します。
"""

# === 基礎定数 (Basic Constants) ===
# 日本の総人口 (2023-2024年基準 / 概算)
NATIONAL_POPULATION = 124_000_000

# 基礎自治体数 (2024年基準)
TOTAL_MUNICIPALITIES = 1_718

# === 計算用派生定数 (Derived Constants) ===
# 標準ブロック人口 (B)
# 計算式: 総人口 / 自治体数 (約72,176人)
STD_BLOCK_POP = NATIONAL_POPULATION / TOTAL_MUNICIPALITIES

# 標準的な単一事業予算の単位 (1,000万円)
# ※予算インパクト計算時の正規化に使用
STD_BUDGET_UNIT = 10_000_000
