from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = Path(r"C:\GNSS_Thesis\results\antarctica_pilot_rf_spectrum_features.csv")
RESULT_FOLDER = Path(r"C:\GNSS_Thesis\results")
FIGURE_FOLDER = Path(r"C:\GNSS_Thesis\figures")

FIGURE_FOLDER.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

print("=" * 70)
print("PILOT DATASET EDA")
print("=" * 70)
print(f"Total rows: {len(df):,}")

print("\nRows by date:")
print(df["date"].value_counts().sort_index())

print("\nLabel counts:")
print(df["jamming_label"].value_counts().sort_index())

features = [
    "agc_count",
    "noise_per_ms",
    "spectrum_mean",
    "spectrum_std",
    "spectrum_max",
    "spectrum_peak_above_median",
    "pga",
]

summary = df.groupby("jamming_label")[features].agg(
    ["count", "mean", "std", "median", "min", "max"]
)
summary_file = RESULT_FOLDER / "pilot_feature_summary_by_jamming_label.csv"
summary.to_csv(summary_file)

print("\nFeature summary by label:")
print(summary)
print(f"\nSaved summary:\n{summary_file}")

jam_day = df[df["date"].astype(str) == "20250324"].copy()

plt.figure(figsize=(12, 4))
plt.plot(jam_day["second_index"], jam_day["jamming_label"], linewidth=0.7)
plt.xlabel("Second index")
plt.ylabel("Jamming label")
plt.yticks([0, 1], ["Normal", "Jamming"])
plt.title("Receiver-Reported Jamming State – 24 March 2025")
plt.tight_layout()
file1 = FIGURE_FOLDER / "F1_jamming_timeline_20250324.png"
plt.savefig(file1, dpi=300)
plt.close()

normal_agc = jam_day.loc[jam_day["jamming_label"] == 0, "agc_count"].dropna()
jam_agc = jam_day.loc[jam_day["jamming_label"] == 1, "agc_count"].dropna()
plt.figure(figsize=(8, 6))
plt.boxplot([normal_agc, jam_agc], tick_labels=["Normal", "Jamming"], showfliers=False)
plt.ylabel("AGC count")
plt.title("AGC Count During Normal and Jamming Periods\n24 March 2025")
plt.tight_layout()
file2 = FIGURE_FOLDER / "F2_agc_normal_vs_jamming.png"
plt.savefig(file2, dpi=300)
plt.close()

normal_noise = jam_day.loc[jam_day["jamming_label"] == 0, "noise_per_ms"].dropna()
jam_noise = jam_day.loc[jam_day["jamming_label"] == 1, "noise_per_ms"].dropna()
plt.figure(figsize=(8, 6))
plt.boxplot([normal_noise, jam_noise], tick_labels=["Normal", "Jamming"], showfliers=False)
plt.ylabel("Noise per millisecond")
plt.title("Receiver Noise During Normal and Jamming Periods\n24 March 2025")
plt.tight_layout()
file3 = FIGURE_FOLDER / "F3_noise_normal_vs_jamming.png"
plt.savefig(file3, dpi=300)
plt.close()

normal_spec = jam_day.loc[jam_day["jamming_label"] == 0, "spectrum_mean"].dropna()
jam_spec = jam_day.loc[jam_day["jamming_label"] == 1, "spectrum_mean"].dropna()
plt.figure(figsize=(8, 6))
plt.boxplot([normal_spec, jam_spec], tick_labels=["Normal", "Jamming"], showfliers=False)
plt.ylabel("Mean spectrum-bin value")
plt.title("Spectrum Level During Normal and Jamming Periods\n24 March 2025")
plt.tight_layout()
file4 = FIGURE_FOLDER / "F4_spectrum_mean_normal_vs_jamming.png"
plt.savefig(file4, dpi=300)
plt.close()

print("\nFigures saved:")
print(file1)
print(file2)
print(file3)
print(file4)
print("\nEDA FINISHED.")
