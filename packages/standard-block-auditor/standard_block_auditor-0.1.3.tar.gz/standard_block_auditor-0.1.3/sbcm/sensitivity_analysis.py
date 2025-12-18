import argparse
import numpy as np
import sys
import os

# 同じフォルダにある config.py を読み込む
try:
    from . import config
except ImportError:
    import config

def run_simulation(v_obs, r_mean, r_sd, population, municipalities, n_sims=20000):
    """
    モンテカルロ・シミュレーションを実行する
    """
    rng = np.random.default_rng(42) # 再現性のためシード固定

    # 1. ターゲット比率 R の不確実性 (正規分布を仮定し、0〜1にクリップ)
    r_samps = rng.normal(loc=r_mean, scale=r_sd, size=n_sims)
    r_samps = np.clip(r_samps, 0.0001, 0.9999) # 0除算防止

    # 2. 発表数値 V の観測誤差 (ポアソン分布を仮定)
    v_samps = rng.poisson(lam=max(1.0, v_obs), size=n_sims)

    # 3. 標準ブロック B と インパクト I の計算
    # config.py の定数ではなく、シミュレーション引数として渡された値（基本はconfigと同じ）を使用
    b_samps = (population * r_samps) / municipalities
    i_samps = v_samps / b_samps

    return i_samps

def main():
    parser = argparse.ArgumentParser(
        description='標準ブロック比較法：堅牢性検証用モンテカルロ・シミュレータ'
    )
    
    parser.add_argument('--value', '-v', type=float, required=True, help='発表された成果数 (V)')
    parser.add_argument('--target_ratio', '-r', type=float, default=1.0, help='ターゲット比率の推定値 (R)')
    parser.add_argument('--ratio_sd', '-sd', type=float, default=0.03, help='ターゲット比率の標準偏差 (不確実性)。デフォルトは0.03')
    parser.add_argument('--sims', type=int, default=20000, help='シミュレーション試行回数')

    args = parser.parse_args()

    # config.py から定数を取得
    pop = config.NATIONAL_POPULATION
    munis = config.TOTAL_MUNICIPALITIES

    print(f"--- Simulation Parameters ---")
    print(f"発表数値 (V): {args.value:,.0f}")
    print(f"ターゲット比率 (R): {args.target_ratio:.2f} (±{args.ratio_sd})")
    print(f"基礎定数 (Pop/Munis): {pop:,.0f} / {munis:,}")
    print(f"試行回数: {args.sims}")
    print(f"-----------------------------")

    try:
        # シミュレーション実行
        i_samps = run_simulation(
            args.value, 
            args.target_ratio, 
            args.ratio_sd, 
            pop, 
            munis, 
            args.sims
        )

        # 統計量の算出
        mean_i = np.mean(i_samps)
        median_i = np.median(i_samps)
        ci_lower, ci_upper = np.percentile(i_samps, [2.5, 97.5]) # 95%信頼区間

        print(f"\n【検証結果】")
        print(f"平均インパクト (Mean I):   {mean_i:.4f}")
        print(f"中央値インパクト (Median I): {median_i:.4f}")
        print(f"95%信頼区間 (95% CI):      [{ci_lower:.4f}, {ci_upper:.4f}]")
        
        print(f"\n【閾値到達確率】")
        thresholds = [1.0, 17.0, 172.0, 859.0]
        labels = ["誤差レベル脱出 (I>=1)", "局所的脱出 (I>=17)", "普及フェーズ (I>=172)", "社会OS (I>=859)"]
        
        for t, label in zip(thresholds, labels):
            prob = np.mean(i_samps >= t)
            print(f"{label}: {prob:.2%}")

        # 最終判定
        if ci_upper < 1.0:
            print(f"\n>>> 結論: 統計的誤差を考慮しても「誤差レベル」であることは確実です。")
        elif ci_lower >= 1.0:
            print(f"\n>>> 結論: 統計的に有意に「誤差レベル」を超えています。")
        else:
            print(f"\n>>> 結論: 評価が分かれる可能性があります（ボーダーライン）。")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
