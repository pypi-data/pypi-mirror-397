# Standard Block Comparison Method (標準ブロック比較法)

[![PyPI version](https://img.shields.io/pypi/v/standard-block-auditor.svg)](https://pypi.org/project/standard-block-auditor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17762960.svg)](https://doi.org/10.5281/zenodo.17762960)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17766254.svg)](https://doi.org/10.5281/zenodo.17766254)

**"数字のマジック"から解き放たれ、行政施策の真の実効性を測るための定量的監査フレームワーク**

A Quantitative Framework for Detecting Budgetary Distortion and Evaluating Administrative Effectiveness.

![SBCM Dashboard Demo](demo_dashboard.png)


## 📖 概要 (Overview)
行政や巨大企業が発表する「累計〇〇人」「予算〇〇億円」といったマクロな数字は、往々にして実態（ROI）を隠蔽するために利用されます。
本プロジェクトでは、これらの数字を「基礎自治体（Standard Block）」という最小単位に正規化し、その施策が社会インフラとして機能しているか、あるいは単なる「統計的誤差」に過ぎないのかを数学的に判定する手法「標準ブロック比較法 (SBCM)」を提供します。

このリポジトリは、SBCMの理論に基づく計算ツール、および行政決算データを解析して「予算の歪み」を検出するPythonライブラリを含みます。

## 🚀 インストール (Installation)

Pythonパッケージとして公開されています。以下のコマンドでインストール可能です。

```bash
pip install standard-block-auditor
```
*(※ パッケージ名を変更して登録した場合は、その名前に置き換えてください)*

## ⚡ クイックスタート (Quick Start)

インストール後、ターミナルから直接コマンドを実行できます。

### 1. 単発の成果数値を検証する (`sbcm-calc`)
行政が発表した「利用者数」や「予算」が、全国規模で見たときにどの程度の影響力を持つか計算します。

```bash
# 例: "利用者3,000人" (ターゲット: 全人口) の場合
sbcm-calc --value 3000 --target_ratio 1.0

# 例: "予算100億円" の場合
sbcm-calc --value 10000000000
```

### 2. 決算書の歪みを検知する (`sbcm-audit`)
決算書データを読み込み、「予算は巨額だが、普及していない事業（第4象限）」を自動検出します。

1.  `example_data.csv` のようなCSVを用意します（AIプロンプト等で作成）。
2.  以下のコマンドを実行します。

```bash
# 自治体の人口を指定して実行 (例: 柏市 43.5万人)
sbcm-audit example_data.csv --pop 435000
```
実行後、分析結果(`distortion_analysis_result.csv`)と可視化グラフ(`distortion_matrix.png`)が出力されます。

### 3. 統計的妥当性を検証する (`sbcm-verify`)
「ターゲット比率の推計が甘いのでは？」という批判に対し、モンテカルロ・シミュレーションを行って結果の堅牢性を証明します。

```bash
# 例: 3,000人、ターゲット比率15% (±3%の誤差を想定)
sbcm-verify --value 3000 --target_ratio 0.15 --ratio_sd 0.03
```

---

## 📐 理論 (Methodology)

### 実効性インパクト ($I$)
施策の到達度を測る指標です。

$$ I = \frac{V}{B} $$

ここで、標準ブロック ($B$) は日本の人口動態と統治機構に基づき以下のように定義されます。

$$ B = \frac{P \times R}{N} $$

*   $P$: 日本の総人口 (1.24億人)
*   $N$: 基礎自治体数 (1,718)
*   $R$: ターゲット属性比率
*   **$B \approx 72,176 \times R$ (人)**

### 判定基準 (The Verdict)
| インパクト値 ($I$) | 判定 | 意味 (Benchmark) |
| :--- | :--- | :--- |
| **$I < 1.0$** | **誤差レベル** | 論外。標準的な1自治体すらカバーできていない。 |
| **$1.0 \le I < 17$** | **局所的** | 実験段階。まだ「アーリーアダプター」にも届いていない。 |
| **$172 \le I < 859$** | **基礎インフラ** | 水道・電気のような社会基盤になりつつある。 |
| **$I \ge 859$** | **社会OS** | 過半数が利用。なくてはならない社会の前提。 |

---

## 📊 予算ポートフォリオ分析 (Budget Portfolio Analysis)

「標準ブロック比較法」を拡張し、「投じられた税金（Budget）」と「得られた成果（Coverage）」のバランスを可視化します。

### 予算歪み指数 ($D_{index}$)
$$ D_{index} = \frac{I_{budget}}{I_{coverage}} $$

この指数に基づき、全事業を4つの象限に分類します。

| 象限 | 状態 | 判定 |
| :--- | :--- | :--- |
| **第1象限** (High Cost / High Reach) | **インフラ** | 適正。金はかかるが全員使う（ゴミ収集、道路）。 |
| **第2象限** (Low Cost / High Reach) | **イノベーション** | 優秀。低予算で広まるDX施策など。 |
| **第4象限** (High Cost / Low Reach) | **【歪み (Distortion)】** | **要監査。巨額の税金が一部にしか届いていない（ハコモノ、利権）。** |

---

## 📂 ディレクトリ構成 (Structure)

```text
Standard-Block-Comparison-Method/
├── sbcm/                  # Pythonパッケージ本体 (Source Code)
│   ├── __init__.py
│   ├── block_calculator.py
│   ├── budget_distortion_analyzer.py
│   ├── sensitivity_analysis.py
│   ├── config.py          # 共通定数定義 (人口、自治体数など)
│   └── visualizer.py      # グラフ描画モジュール
│
├── prompts/               # AI監査官プロンプト (Prompt Engineering)
├── reports/               # ケーススタディ・論文素材
├── example_data.csv       # サンプルデータ
├── google_sheets_script.js # Googleスプレッドシート用スクリプト
├── pyproject.toml         # パッケージ設定
└── README.md              # 本ドキュメント
```

## 📝 ライセンス (License)

本プロジェクトは [MIT License](LICENSE) の下で公開されています。
誰でも自由に行政データの検証・監査に利用できます。

---

### Author
**Melnus** (GitHub: [Melnus](https://github.com/Melnus))

## 📝 Citation
If you use SBCM in your research or auditing, please cite the following paper:

> Koyama, H. (2025). Proposal for the Standard Block Comparison Method (SBCM) in the Quantitative Evaluation of Administrative Measures. Zenodo. https://doi.org/10.5281/zenodo.17762960
