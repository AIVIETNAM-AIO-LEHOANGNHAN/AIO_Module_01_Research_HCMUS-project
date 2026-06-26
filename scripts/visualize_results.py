import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from scripts.paths import DOCS_DIR


# ======================================================
# 1. LOAD RESULTS
# ======================================================
def load_results(file_path):
    """
    Đọc file kết quả threshold experiment
    """
    return pd.read_csv(file_path)


# ======================================================
# 2. CREATE SUMMARY TABLE
# ======================================================
def create_summary_table(df, output_dir):
    """
    Tạo bảng tổng hợp accuracy & f1 theo threshold
    """

    summary = df.pivot_table(
        index="threshold",
        columns="experiment",
        values=["accuracy", "f1"]
    )

    output_path = Path(output_dir) / "summary_table.md"

    summary.to_markdown(output_path)

    print(f"Saved summary table → {output_path}")


# ======================================================
# 3. PLOT METRICS
# ======================================================
def plot_metric(df, metric, output_dir, style="o"):
    """
    Vẽ biểu đồ so sánh giữa các experiment
    """

    plt.figure(figsize=(10, 6))

    sns.lineplot(
        data=df,
        x="threshold",
        y=metric,
        hue="experiment",
        marker=style
    )

    plt.title(f"So sánh {metric.upper()} theo Threshold")
    plt.xlabel("Threshold")
    plt.ylabel(metric.upper())
    plt.grid(True)

    output_path = Path(output_dir) / f"{metric}_comparison.png"
    plt.savefig(output_path)

    print(f"Saved plot → {output_path}")


# ======================================================
# 4. MAIN VISUALIZATION PIPELINE
# ======================================================
def visualize_results():

    # -------------------------
    # load data
    # -------------------------
    file_path = Path(DOCS_DIR) / "threshold_results.csv"
    df = load_results(file_path)

    # -------------------------
    # create report table
    # -------------------------
    create_summary_table(df, DOCS_DIR)

    # -------------------------
    # plots
    # -------------------------
    plot_metric(df, "accuracy", DOCS_DIR, style="o")
    plot_metric(df, "f1", DOCS_DIR, style="s")


# ======================================================
# 5. ENTRY POINT
# ======================================================
if __name__ == "__main__":
    visualize_results()