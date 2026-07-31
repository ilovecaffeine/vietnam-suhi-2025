"""
create_statistics.py

Generate descriptive statistics, spatial statistics, bootstrap confidence
intervals, and visualizations for Surface Urban Heat Island (SUHI).

Outputs
-------
- suhi_results.xlsx
- suhi_histogram.png
- suhi_vs_area_scatter.png
- moran_scatter.png
- urban_zones_lisa.geojson
"""

# ============================================================
# Imports
# ============================================================
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from esda.moran import Moran
from libpysal.weights import KNN
from libpysal.weights import lag_spatial
from esda.moran import Moran_Local

# ============================================================
# Project directories
# ============================================================
ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RESULT_DIR = DATA_DIR / "results"
FIGURE_DIR = ROOT_DIR / "figures"

# ============================================================
# Input and output files
# ============================================================
input_geojson = RESULT_DIR / "urban_zones_suhi.geojson"

output_excel = RESULT_DIR / "suhi_results.xlsx"
output_hist_png = FIGURE_DIR / "suhi_histogram.png"
output_scatter_png = FIGURE_DIR / "suhi_vs_area_scatter.png"
output_moran_png = FIGURE_DIR / "moran_scatter.png"

# ============================================================
# Load data
# ============================================================
print("Loading urban zones...")

gdf = gpd.read_file(input_geojson)

# Keep required columns
df = gdf[
    [
        "zone_id",
        "centroid_lon",
        "centroid_lat",
        "area_km2",
        "urban_mean_C",
        "rural_mean_C",
        "suhi_C",
    ]
].copy()

df = df.sort_values("zone_id").reset_index(drop=True)

# ============================================================
# Descriptive statistics
# ============================================================
# Valid SUHI values
suhi_data = df["suhi_C"].dropna()

# Summary statistics
summary = pd.DataFrame(
    {
        "Statistic": [
            "Urban zones",
            "Mean SUHI (°C)",
            "Median SUHI (°C)",
            "Standard deviation (°C)",
            "Minimum (°C)",
            "Maximum (°C)",
            "Q1 (25%)",
            "Q3 (75%)",
            "Positive SUHI (>0°C)",
            "Negative SUHI (<0°C)",
            "Mean Urban LST (°C)",
            "Mean Rural LST (°C)",
        ],
        "Value": [
            len(df),
            suhi_data.mean(),
            suhi_data.median(),
            suhi_data.std(),
            suhi_data.min(),
            suhi_data.max(),
            suhi_data.quantile(0.25),
            suhi_data.quantile(0.75),
            (suhi_data > 0).sum(),
            (suhi_data < 0).sum(),
            df["urban_mean_C"].mean(),
            df["rural_mean_C"].mean(),
        ],
    }
)

summary["Value"] = summary["Value"].round(2)

# ============================================================
# Top 10 highest and lowest SUHI zones
# ============================================================
top_high = (
    df.sort_values("suhi_C", ascending=False)
      .head(10)
      .reset_index(drop=True)
)

top_high.insert(0, "Rank", range(1, len(top_high) + 1))

top_low = (
    df.sort_values("suhi_C", ascending=True)
      .head(10)
      .reset_index(drop=True)
)

top_low.insert(0, "Rank", range(1, len(top_low) + 1))

# ============================================================
# Global Moran's I
# ============================================================
print("\n🌍 Calculating Global Moran's I...")

# Keep valid polygons only
gdf_moran = gdf[
    [
        "geometry",
        "suhi_C",
    ]
].dropna().reset_index(drop=True).copy()

# Spatial weights: KNN (k = 5)
w = KNN.from_dataframe(
    gdf_moran,
    k=5,
)

# Row standardization
w.transform = "R"

# SUHI values
y = gdf_moran["suhi_C"].values

# Moran's I
mi = Moran(
    y,
    w,
    permutations=999,
)

# Display Moran's I statistics
z_val = mi.z_sim
p_val = mi.p_sim  # Or mi.p_norm
p_str = "< 0.001" if p_val < 0.001 else f"{p_val:.4f}"

print(f"Number of zones = {len(gdf_moran)}")
print(f"Moran's I      = {mi.I:.4f}")
print(f"Expected I     = {mi.EI:.4f}")
print(f"z-score        = {z_val:.4f}")
print(f"p-value        = {p_str}")

moran_table = pd.DataFrame(
    {
        "Statistic": [
            "Number of zones",
            "Spatial weights",
            "Neighbors (k)",
            "Moran's I",
            "Expected I",
            "z-score",
            "p-value",
        ],
        "Value": [
            str(len(gdf_moran)),
            "KNN",
            "5",
            f"{mi.I:.4f}",
            f"{mi.EI:.4f}",
            f"{z_val:.4f}",
            "< 0.001" if p_val < 0.001 else f"{p_val:.4f}",
        ],
    }
)

# ============================================================
# Local Indicators of Spatial Association (LISA)
# ============================================================
print("\n📍 Calculating Local Moran's I...")

lisa = Moran_Local(
    y,
    w,
    permutations=999,
)

gdf_moran["local_I"] = lisa.Is
gdf_moran["p_value"] = lisa.p_sim
gdf_moran["quadrant"] = lisa.q

alpha = 0.05

gdf_moran["cluster"] = "Not Significant"

sig = lisa.p_sim < alpha

gdf_moran.loc[sig & (lisa.q == 1), "cluster"] = "High-High"
gdf_moran.loc[sig & (lisa.q == 2), "cluster"] = "Low-High"
gdf_moran.loc[sig & (lisa.q == 3), "cluster"] = "Low-Low"
gdf_moran.loc[sig & (lisa.q == 4), "cluster"] = "High-Low"

cluster_summary = (
    gdf_moran["cluster"]
    .value_counts()
    .rename_axis("Cluster")
    .reset_index(name="Count")
)

print(cluster_summary)

gdf_lisa = gdf.merge(
    gdf_moran[
        [
            "local_I",
            "p_value",
            "cluster",
        ]
    ],
    left_index=True,
    right_index=True,
)

gdf_lisa.to_file(
    RESULT_DIR / "urban_zones_lisa.geojson",
    driver="GeoJSON",
)

# ============================================================
# Bootstrap confidence interval for mean SUHI
# ============================================================
print("\n🔄 Bootstrap Mean SUHI...")

N_BOOT = 5000
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)

boot_means = np.empty(N_BOOT)

values = suhi_data.to_numpy()

for i in range(N_BOOT):

    sample = rng.choice(
        values,
        size=len(values),
        replace=True,
    )

    boot_means[i] = sample.mean()

# Bootstrap statistics
boot_mean = boot_means.mean()
boot_std = boot_means.std(ddof=1)

ci95_low = np.percentile(
    boot_means,
    2.5,
)

ci95_high = np.percentile(
    boot_means,
    97.5,
)

bootstrap_summary = pd.DataFrame(
    {
        "Statistic": [
            "Observed mean",
            "Bootstrap mean",
            "Bootstrap std",
            "95% CI lower",
            "95% CI upper",
            "Bootstrap iterations",
        ],
        "Value": [
            f"{values.mean():.4f}",
            f"{boot_mean:.4f}",
            f"{boot_std:.4f}",
            f"{ci95_low:.4f}",
            f"{ci95_high:.4f}",
            N_BOOT,
        ],
    }
)

# ============================================================
# Urban–rural thermal contribution analysis
# ============================================================
mean_urban = df["urban_mean_C"].mean()
mean_rural = df["rural_mean_C"].mean()

df_contribution = df[
    [
        "zone_id",
        "urban_mean_C",
        "rural_mean_C",
        "suhi_C",
    ]
].copy()

df_contribution["urban_contribution"] = (
    df_contribution["urban_mean_C"] - mean_urban
)

df_contribution["rural_contribution"] = (
    mean_rural - df_contribution["rural_mean_C"]
)

EPS = 0.5
def sign3(x):
    if x > EPS:
        return "+"
    elif x < -EPS:
        return "-"
    else:
        return "≈0"

df_contribution["SUHI_sign"] = (
    df_contribution["suhi_C"]
    .apply(sign3)
)

df_contribution["Urban_sign"] = (
    df_contribution["urban_contribution"]
    .apply(sign3)
)

df_contribution["Rural_sign"] = (
    df_contribution["rural_contribution"]
    .apply(sign3)
)

case_count = (
    df_contribution.groupby(
        [
            "SUHI_sign",
            "Urban_sign",
            "Rural_sign",
        ]
    )
    .size()
    .reset_index(name="Count")
)

cases = [
    ("+", "+", "+"),
    ("+", "+", "≈0"),
    ("+", "≈0", "+"),
    ("+", "-", "≈0"),
    ("+", "≈0", "-"),
    ("+", "≈0", "≈0"),
    ("+", "+", "-"),
    ("+", "-", "+"),
    ("+", "-", "-"),

    ("-", "-", "-"),
    ("-", "-", "≈0"),
    ("-", "≈0", "-"),
    ("-", "+", "≈0"),
    ("-", "≈0", "+"),
    ("-", "≈0", "≈0"),
    ("-", "+", "-"),
    ("-", "-", "+"),
]

case_table = pd.DataFrame(
    cases,
    columns=[
        "SUHI",
        "Urban",
        "Rural",
    ],
)

case_table = case_table.merge(
    case_count,
    left_on=[
        "SUHI",
        "Urban",
        "Rural",
    ],
    right_on=[
        "SUHI_sign",
        "Urban_sign",
        "Rural_sign",
    ],
    how="left",
)

case_table["Count"] = (
    case_table["Count"]
    .fillna(0)
    .astype(int)
)

case_table = case_table[
    [
        "SUHI",
        "Urban",
        "Rural",
        "Count",
    ]
]

case_table = (
    case_table.query("Count > 0")
    .reset_index(drop=True)
)

print("\nSUHI sign counts")
print(df_contribution["SUHI_sign"].value_counts())

# ============================================================
# Export Excel report
# ============================================================
print("Writing Excel report...")

with pd.ExcelWriter(
    output_excel,
    engine="openpyxl",
) as writer:

    df.to_excel(
        writer,
        sheet_name="Urban_Zones",
        index=False,
    )

    summary.to_excel(
        writer,
        sheet_name="Summary",
        index=False,
    )

    top_high.to_excel(
        writer,
        sheet_name="Top_SUHI_High",
        index=False,
    )

    top_low.to_excel(
        writer,
        sheet_name="Top_SUHI_Low",
        index=False,
    )

    moran_table.to_excel(
        writer,
        sheet_name="Moran_I",
        index=False,
    )

    cluster_summary.to_excel(
    writer,
    sheet_name="LISA_Summary",
    index=False,
    )

    bootstrap_summary.to_excel(
    writer,
    sheet_name="Bootstrap_Mean",
    index=False,
    )

    df_contribution.to_excel(
    writer,
    sheet_name="Contribution",
    index=False,
    )

    case_table.to_excel(
    writer,
    sheet_name="Contribution_Cases",
    index=False,
    )

# Save workbook
print(f"Saved: {output_excel}")

# ============================================================
# SUHI histogram
# ============================================================
print("\n📈 Creating SUHI Histogram...")

if not suhi_data.empty:

    plt.figure(figsize=(10, 6))

    # 1°C bins
    min_val = np.floor(suhi_data.min())
    max_val = np.ceil(suhi_data.max())

    bins = np.arange(min_val, max_val + 1, 1)

    plt.hist(
        suhi_data,
        bins=bins,
        color="crimson",
        edgecolor="black",
        alpha=0.7,
    )

    # Mean line
    mean_val = suhi_data.mean()

    plt.axvline(
        mean_val,
        color="blue",
        linestyle="--",
        linewidth=2,
        label=f"Mean = {mean_val:.2f}°C",
    )

    # Median line
    median_val = suhi_data.median()

    plt.axvline(
        median_val,
        color="green",
        linestyle="-.",
        linewidth=2,
        label=f"Median = {median_val:.2f}°C",
    )

    plt.xticks(bins)

    plt.title(
        "Distribution of Surface Urban Heat Island Intensity (SUHI)",
        fontsize=14,
        fontweight="bold",
    )

    plt.xlabel("SUHI (°C)")
    plt.ylabel("Number of Urban Zones")

    plt.grid(axis="y", alpha=0.3)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_hist_png,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Saved: {output_hist_png}")

    plt.show()

else:

    print("No valid SUHI data available.")

# ============================================================
# Area vs SUHI scatter (Spearman)
# ============================================================
print("\n📊 Creating urban area vs SUHI scatter plot...")

scatter_df = df[
    [
        "area_km2",
        "suhi_C",
    ]
].dropna()

if len(scatter_df) > 2:

    rho, p_value = spearmanr(
        scatter_df["area_km2"],
        scatter_df["suhi_C"],
    )

    plt.figure(figsize=(7, 6))

    plt.scatter(
        scatter_df["area_km2"],
        scatter_df["suhi_C"],
        s=35,
        alpha=0.7,
    )

    plt.xlabel("Urban Area (km²)")
    plt.ylabel("SUHI (°C)")

    plt.title(
        "Relationship between Urban Area and SUHI",
        fontsize=13,
        fontweight="bold",
    )

    plt.grid(alpha=0.3)
    
    # Fixed axis limit for consistency
    plt.xlim(0, 120)
    
    plt.text(
    0.98,
    0.98,
    f"Spearman ρ = {rho:.3f}\np-value = {p_value:.4f}",
    transform=plt.gca().transAxes,
    horizontalalignment="right",
    verticalalignment="top",
    bbox=dict(
        facecolor="white",
        alpha=0.8,
    ),
)

    plt.tight_layout()

    plt.savefig(
        output_scatter_png,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Saved: {output_scatter_png}")
    print(f"Spearman rho = {rho:.3f}")
    print(f"p-value = {p_value:.6f}")

    plt.show()

else:

    print("Not enough data to calculate Spearman correlation.")

# ============================================================
# Moran scatter plot (standardized z-score)
# ============================================================
print("Creating Moran scatter plot...")

# Standardize SUHI
z_y = (y - y.mean()) / y.std(ddof=1)

# Compute spatial lag
z_lag_y = lag_spatial(w, z_y)

plt.figure(figsize=(7, 7))

# Plot points
plt.scatter(z_y, z_lag_y, alpha=0.6, color="#1f77b4", edgecolors="none", s=30)

# Fitted line
xfit = np.linspace(z_y.min(), z_y.max(), 200)

plt.plot(
    xfit,
    mi.I * xfit,
    color="#d62728",
    linewidth=2,
    label=f"Slope = Moran's I ({mi.I:.3f})",
)

# Quadrant axes
plt.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
plt.axvline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)

xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()

plt.text(
    xmax * 0.95,
    ymax * 0.95,
    "HH",
    ha="right",
    va="top",
    fontsize=11,
    fontweight="bold",
)

plt.text(
    xmin * 0.95,
    ymax * 0.80,
    "LH",
    ha="left",
    va="top",
    fontsize=11,
    fontweight="bold",
)

plt.text(
    xmin * 0.95,
    ymin * 0.95,
    "LL",
    ha="left",
    va="bottom",
    fontsize=11,
    fontweight="bold",
)

plt.text(
    xmax * 0.95,
    ymin * 0.95,
    "HL",
    ha="right",
    va="bottom",
    fontsize=11,
    fontweight="bold",
)

# Axis labels
plt.xlabel("SUHI (Attribute z-score)", fontsize=11, fontweight="bold")
plt.ylabel(
    "Spatial Lag of SUHI (Spatial lag z-score)", fontsize=11, fontweight="bold"
)

plt.title(
    "Global Moran Scatter Plot",
    fontsize=13,
    fontweight="bold",
    pad=12,
)

# Stats textbox
p_text = "p < 0.001" if p_val < 0.001 else f"p = {p_val:.4f}"

plt.text(
    0.03,
    0.97,  # Place box in the upper-left corner
    f"Moran's I = {mi.I:.3f}\n{p_text}",
    transform=plt.gca().transAxes,
    horizontalalignment="left",
    verticalalignment="top",
    fontsize=10,
    bbox=dict(
        facecolor="white",
        edgecolor="gray",
        alpha=0.85,
        boxstyle="round,pad=0.5",
    ),
)

plt.grid(alpha=0.2, linestyle=":")
plt.tight_layout()

plt.savefig(output_moran_png, dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved: {output_moran_png}")
