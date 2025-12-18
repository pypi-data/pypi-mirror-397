import argparse
import sys
import os

# 同じフォルダにある config.py を読み込む
try:
    from . import config
except ImportError:
    import config

def calculate_standard_block(population, target_ratio, municipalities):
    """
    標準ブロック（1自治体あたりの平均ターゲット数）を算出する
    """
    return (population * target_ratio) / municipalities

def calculate_impact(value, standard_block):
    """
    実効性インパクト（I）を算出する
    """
    if standard_block == 0:
        return 0
    return value / standard_block

def get_verdict(impact):
    """
    インパクト値に基づいて、詳細な「社会実装ステージ」を判定する
    NOTE: I値は「いくつの自治体を満杯にできるか」を示す。Maxは1718。
    """
    if impact < 1.0:
        return "💀【誤差レベル (Error)】\n   判定: 1自治体すらカバーできていません。社会インフラとして機能不全です。"
    
    elif impact < 17.2:
        return "⚠️【局所的 (Localized)】\n   判定: 全国普及率1%未満。一部地域での実験、またはマニア向け段階です。"
    
    elif impact < 172.0:
        return "🚀【普及フェーズ (Early Majority)】\n   判定: 全国普及率1%〜10%。「クラスに1人」程度まで浸透しています。"
    
    elif impact < 859.0:
        return "🏠【基礎インフラ級 (Infrastructure)】\n   判定: 全国普及率10%〜50%。生活に定着しつつある準インフラです。"
    
    else:
        return "👑【社会OS級 (Social OS)】\n   判定: 全国普及率50%以上。なくてはならない社会基盤です。"

def main():
    parser = argparse.ArgumentParser(
        description='標準ブロック比較法 (Standard Block Comparison Method) 計算ツール v2.2'
    )
    
    # 必須引数
    parser.add_argument(
        '--value', '-v',
        type=float,
        required=True,
        help='発表された成果数（例: 利用者数3000人なら 3000、予算1億円なら 100000000）'
    )

    # オプション引数
    parser.add_argument(
        '--target_ratio', '-r',
        type=float,
        default=1.0,
        help='ターゲット属性の比率 (0.0 〜 1.0)。デフォルトは1.0（全人口）'
    )
    
    parser.add_argument(
        '--population', '-p',
        type=int,
        default=config.NATIONAL_POPULATION,
        help=f'総人口。デフォルトは {config.NATIONAL_POPULATION:,}'
    )
    
    parser.add_argument(
        '--municipalities', '-m',
        type=int,
        default=config.TOTAL_MUNICIPALITIES,
        help=f'基礎自治体数。デフォルトは {config.TOTAL_MUNICIPALITIES:,}'
    )

    args = parser.parse_args()

    # 計算実行
    try:
        standard_block = calculate_standard_block(
            args.population, 
            args.target_ratio, 
            args.municipalities
        )
        
        impact = calculate_impact(args.value, standard_block)
        
        # 結果表示
        print("\n=== 標準ブロック比較法 分析結果 (v2.2) ===")
        print(f"1. 入力値 (Value):       {args.value:,.0f}")
        print(f"2. ターゲット比率:       {args.target_ratio * 100:.1f}%")
        print("-" * 40)
        print(f"3. 標準ブロック (B):     {standard_block:,.1f} (1自治体あたりのキャパシティ)")
        print(f"4. 実効性インパクト (I): {impact:.4f} ブロック")
        print("-" * 40)
        print(f"結論: {get_verdict(impact)}")
        print("========================================\n")

    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
