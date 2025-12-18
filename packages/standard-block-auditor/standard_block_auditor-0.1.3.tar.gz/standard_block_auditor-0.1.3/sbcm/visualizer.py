import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys
import os

# 日本語フォント設定（環境に合わせて調整が必要な場合があります）
# Windows: 'Meiryo', Mac: 'Hiragino Sans', Linux: 'IPAGothic' など
try:
    if os.name == 'nt': # Windows
        plt.rcParams['font.family'] = 'Meiryo'
    elif sys.platform == 'darwin': # Mac
        plt.rcParams['font.family'] = 'Hiragino Sans'
    else:
        plt.rcParams['font.family'] = 'IPAGothic'
except Exception:
    print("日本語フォントが見つかりません。豆腐（□）になる可能性があります。")

def plot_distortion_matrix(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"CSV読み込みエラー: {e}")
        sys.exit(1)

    # グラフ設定
    plt.figure(figsize=(10, 8))
    
    # 軸の定義
    # X軸: 普及インパクト (I_coverage) - 対数軸推奨
    # Y軸: 予算インパクト (I_budget) - 対数軸推奨
    x = df['普及Imp']
    y = df['予算Imp']
    z = df['歪み指数(D)'] # バブルの大きさ
    labels = df['事業名']

    # 散布図描画 (歪み指数が大きいほどバブルを大きく、色を赤く)
    # s=バブルサイズ, c=色(歪み指数に基づく), cmap=カラーマップ, alpha=透明度
    scatter = plt.scatter(x, y, s=z*10, c=z, cmap='coolwarm', alpha=0.6, edgecolors="grey", linewidth=1)

    # 象限の境界線（基準値 = 1.0）
    plt.axvline(x=1.0, color='gray', linestyle='--', linewidth=1)
    plt.axhline(y=1.0, color='gray', linestyle='--', linewidth=1)

    # ラベル付与
    for i, label in enumerate(labels):
        # データポイントの近くにテキストを表示
        plt.text(x[i], y[i], label, fontsize=9, ha='right', va='bottom')

    # 装飾
    plt.title('予算歪みマトリクス (Budget Distortion Matrix)', fontsize=14)
    plt.xlabel('普及インパクト (人数) →', fontsize=12)
    plt.ylabel('予算インパクト (金額) →', fontsize=12)
    
    # 対数軸に設定（重要：スケールの違いを吸収するため）
    plt.xscale('log')
    plt.yscale('log')
    
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    # 象限の注釈（座標は対数軸上の目安位置）
    plt.text(0.01, 100, '【第4象限】\n異常な歪み\n(高コスト・低普及)', color='red', fontsize=12, fontweight='bold', ha='left', va='top')
    plt.text(100, 0.01, '【第2象限】\nイノベーション\n(低コスト・高普及)', color='blue', fontsize=12, fontweight='bold', ha='right', va='bottom')

    # カラーバー
    cbar = plt.colorbar(scatter)
    cbar.set_label('歪み指数 (Distortion Index)')

    # 画像保存
    output_img = 'distortion_matrix.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"グラフを保存しました: {output_img}")
    
    # 実行環境によってはウィンドウを表示（必要ならコメントアウト解除）
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualizer.py <input_csv_file>")
        print("Example: python visualizer.py distortion_analysis_result.csv")
    else:
        plot_distortion_matrix(sys.argv[1])
