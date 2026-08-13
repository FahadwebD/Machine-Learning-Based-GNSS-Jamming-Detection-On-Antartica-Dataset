from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, average_precision_score, roc_auc_score

DATA_FILE = Path(r"C:\GNSS_Thesis\results\antarctica_pilot_combined_features.csv")
RESULT_FOLDER = Path(r"C:\GNSS_Thesis\results")
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

BLOCK_SECONDS = 600

FEATURES = [
    "measx_sat_count_mean",
    "measx_cno_max",
    "measx_abs_doppler_mean",
    "measx_cno_std",
    "measx_cno_min",
    "noise_per_ms",
    "spectrum_std",
    "measx_cno_median",
    "spectrum_peak_above_median",
    "spectrum_max",
]


def metrics(y_true, y_pred, y_prob):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    far = fp / (fp + tn) if (fp + tn) else np.nan
    mdr = fn / (fn + tp) if (fn + tp) else np.nan
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "false_alarm_rate": far,
        "missed_detection_rate": mdr,
        "pr_auc": average_precision_score(y_true, y_prob),
        "roc_auc": roc_auc_score(y_true, y_prob),
    }


def main():
    df = pd.read_csv(DATA_FILE)
    df["date"] = df["date"].astype(str)
    march = df[df["date"] == "20250324"].copy()
    march = march.sort_values("second_index").reset_index(drop=True)
    march["temporal_group"] = (march["second_index"] // BLOCK_SECONDS).astype(int)

    print("=" * 78)
    print("STEP 7 - GROUPED TEMPORAL VALIDATION")
    print("=" * 78)
    print(f"24 March observations: {len(march):,}")
    print(f"Temporal block size: {BLOCK_SECONDS} seconds ({BLOCK_SECONDS // 60} minutes)")
    print(f"Number of temporal groups: {march['temporal_group'].nunique()}")

    X = march[FEATURES]
    y = march["jamming_label"]
    groups = march["temporal_group"]

    models = {
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ]),
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1)),
        ]),
    }

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    fold_rows = []
    summary_rows = []

    for model_name, base_model in models.items():
        print("\n" + "=" * 78)
        print(model_name)
        print("=" * 78)
        current = []

        for fold, (train_idx, test_idx) in enumerate(cv.split(X, y, groups), start=1):
            train_groups = set(groups.iloc[train_idx])
            test_groups = set(groups.iloc[test_idx])
            overlap = train_groups.intersection(test_groups)
            assert len(overlap) == 0, "Temporal group leakage detected"

            model = clone(base_model)
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            pred = model.predict(X.iloc[test_idx])
            prob = model.predict_proba(X.iloc[test_idx])[:, 1]
            row = metrics(y.iloc[test_idx], pred, prob)
            row.update({
                "model": model_name,
                "fold": fold,
                "train_rows": len(train_idx),
                "test_rows": len(test_idx),
                "train_groups": len(train_groups),
                "test_groups": len(test_groups),
                "group_overlap": len(overlap),
            })
            fold_rows.append(row)
            current.append(row)
            print(f"Fold {fold}: overlap={len(overlap)} | accuracy={row['accuracy']:.4f} | F1={row['f1']:.4f} | FAR={row['false_alarm_rate']:.4f}")

        current_df = pd.DataFrame(current)
        summary_rows.append({
            "model": model_name,
            "accuracy_mean": current_df["accuracy"].mean(),
            "accuracy_std": current_df["accuracy"].std(),
            "balanced_accuracy_mean": current_df["balanced_accuracy"].mean(),
            "precision_mean": current_df["precision"].mean(),
            "recall_mean": current_df["recall"].mean(),
            "f1_mean": current_df["f1"].mean(),
            "f1_std": current_df["f1"].std(),
            "false_alarm_rate_mean": current_df["false_alarm_rate"].mean(),
            "missed_detection_rate_mean": current_df["missed_detection_rate"].mean(),
            "pr_auc_mean": current_df["pr_auc"].mean(),
            "roc_auc_mean": current_df["roc_auc"].mean(),
        })

    fold_df = pd.DataFrame(fold_rows)
    summary_df = pd.DataFrame(summary_rows)
    fold_file = RESULT_FOLDER / "grouped_validation_fold_results.csv"
    summary_file = RESULT_FOLDER / "grouped_validation_summary.csv"
    fold_df.to_csv(fold_file, index=False)
    summary_df.to_csv(summary_file, index=False)

    print("\n" + "=" * 78)
    print("GROUPED VALIDATION SUMMARY")
    print("=" * 78)
    print(summary_df.round(4).to_string(index=False))

    random_file = RESULT_FOLDER / "pilot_ml_random_split_metrics.csv"
    if random_file.exists():
        random_df = pd.read_csv(random_file)[["model", "accuracy", "precision", "recall", "f1", "false_alarm_rate"]].copy()
        random_df.columns = ["model", "random_accuracy", "random_precision", "random_recall", "random_f1", "random_false_alarm"]
        grouped_df = summary_df[["model", "accuracy_mean", "precision_mean", "recall_mean", "f1_mean", "false_alarm_rate_mean"]]
        comparison = pd.merge(random_df, grouped_df, on="model")
        comparison_file = RESULT_FOLDER / "random_vs_grouped_validation.csv"
        comparison.to_csv(comparison_file, index=False)
        print("\n" + "=" * 78)
        print("RANDOM SPLIT VS GROUPED TEMPORAL VALIDATION")
        print("=" * 78)
        print(comparison.round(4).to_string(index=False))
        print(f"\nSaved comparison: {comparison_file}")

    print("\nCritical leakage check:")
    print("Every fold had group_overlap = 0.")
    print("No 10-minute temporal group appeared in both training and testing.")
    print("\nSTEP 7 FINISHED.")


if __name__ == "__main__":
    main()
