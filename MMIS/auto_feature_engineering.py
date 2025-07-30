import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest


def auto_feature_engineering(df, output_dir="outputs", n_top_features=10):
    os.makedirs(output_dir, exist_ok=True)

    report = {}

    # ===================== 1. Summary Stats =====================
    summary_stats = df.describe(include='all').transpose()
    summary_stats.to_csv(os.path.join(output_dir, "summary_statistics.csv"))
    report["summary_stats"] = "Saved summary_statistics.csv"

    # ===================== 2. Missing Values =====================
    missing = df.isnull().sum().sort_values(ascending=False)
    missing_percent = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_percent
    })
    missing_df = missing_df[missing_df["Missing Count"] > 0]
    missing_df.to_csv(os.path.join(output_dir, "missing_values.csv"))
    report["missing_values"] = "Saved missing_values.csv"

    # ===================== 3. Correlation Heatmap =====================
    numeric_df = df.select_dtypes(include=np.number).dropna(axis=1, how="any")
    corr = numeric_df.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()
    report["correlation_heatmap"] = "Saved correlation_heatmap.png"

    # ===================== 4. Variance Ranking =====================
    variances = numeric_df.var().sort_values(ascending=False)
    top_vars = variances.head(n_top_features)
    top_vars.to_csv(os.path.join(output_dir, "top_variance_features.csv"))
    report["top_variance_features"] = "Saved top_variance_features.csv"

    # ===================== 5. PCA =====================
    if numeric_df.shape[1] > 1:
        scaled = StandardScaler().fit_transform(numeric_df.fillna(0))
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled)
        pca_df = pd.DataFrame(pca_result, columns=["PC1", "PC2"])
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x="PC1", y="PC2", data=pca_df, alpha=0.6)
        plt.title("PCA Projection (2D)")
        plt.tight_layout()
        pca_path = os.path.join(output_dir, "pca_projection.png")
        plt.savefig(pca_path)
        plt.close()
        report["pca_projection"] = "Saved pca_projection.png"

    # ===================== 6. Isolation Forest (Optional) =====================
    try:
        clf = IsolationForest(contamination=0.05, random_state=42)
        numeric_df = numeric_df.fillna(numeric_df.mean())
        clf.fit(numeric_df)
        df["Outlier"] = clf.predict(numeric_df)
        outlier_count = (df["Outlier"] == -1).sum()
        report["outlier_detection"] = f"Detected {outlier_count} outliers"
        df.to_csv(os.path.join(output_dir, "with_outlier_flag.csv"), index=False)
    except:
        report["outlier_detection"] = "Isolation Forest failed on this data."

    # ===================== 7. Automated Plots =====================
    for col in numeric_df.columns[:n_top_features]:
        plt.figure()
        sns.histplot(df[col].dropna(), kde=True, bins=30)
        plt.title(f"Distribution: {col}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"dist_{col}.png"))
        plt.close()

    return report
