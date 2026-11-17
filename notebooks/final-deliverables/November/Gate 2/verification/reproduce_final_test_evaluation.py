"""Independent reproduction of November Gate 2 (Jonathan's final test evaluation).

Follows the 8 review checks in frozen_final_evaluation_plan.md. Loads the saved
model only (no fit), scores the test partition, and compares with saved outputs.
Usage: python -I reproduce_final_test_evaluation.py <repo_root> <test_evaluation_outputs_dir>
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

repo, outdir = Path(sys.argv[1]), Path(sys.argv[2])
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


frozen = {
    "data/allstate_claims_data.csv": "74037cb248a1064e4d578692a4f4e5d8492ed1b2033daf643496e1b68b14ae03",
    "notebooks/final-deliverables/October/Gate 1/partition_manifest.csv": "de10b0e17ad56174a7b126352a0a41b3b3d477bbddd65f37b87a6235f582a64b",
    "notebooks/liam-stapley/model_experiment_outputs/final_top75_catboost_model.cbm": "f2e364cf596c5fb6b36a7508b439a3f14a11e42b8a3faa3249543f70bfc8a27c",
    "notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv": "b960c7574527e4f0bc7785353006f99c8d973be320efbe248ec9a5c55e99c2c0",
    "notebooks/final-deliverables/October/Gate 1/high_loss_support.csv": "043462ad0f3c5ac28d2467ec259c1c4e2aa340f6b2be385c04f36ee2f7df08d9",
}
# 1. hashes and partition counts
for rel, h in frozen.items():
    check(f"hash {Path(rel).name}", sha(repo / rel) == h)

data = pd.read_csv(repo / "data/allstate_claims_data.csv")
manifest = pd.read_csv(repo / "notebooks/final-deliverables/October/Gate 1/partition_manifest.csv")
counts = manifest["partition"].value_counts().to_dict()
check("partition counts", counts == {"train": 131822, "validation": 28248, "test": 28248}, str(counts))
df = data.merge(manifest[["id", "partition"]], on="id", how="inner", validate="one_to_one")
check("manifest covers all rows", len(df) == len(data) == 188318)
train = df[df.partition == "train"]
test = df[df.partition == "test"].sort_values("id").reset_index(drop=True)

# 5. model and features match plan
features = pd.read_csv(repo / "notebooks/liam-stapley/model_experiment_outputs/final_catboost_features.csv")["feature"].tolist()
cat_cols = [f for f in features if f.startswith("cat")]
check("75 unique features, 61 categorical", len(set(features)) == 75 and len(cat_cols) == 61)
model = CatBoostRegressor()
model.load_model(str(repo / "notebooks/liam-stapley/model_experiment_outputs/final_top75_catboost_model.cbm"))
params = model.get_all_params()
check("model config", params["loss_function"] == "MAE" and params["depth"] == 8
      and abs(params["learning_rate"] - 0.08) < 1e-6 and model.tree_count_ == 500 and params["random_seed"] == 42,
      f"loss={params['loss_function']} depth={params['depth']} lr={params['learning_rate']:.4f} trees={model.tree_count_}")
check("model feature order matches list", list(model.feature_names_) == features)

# 7. fresh deterministic inference (no fit)
X = test[features].copy()
for c in cat_cols:
    X[c] = X[c].astype(str)
fresh = model.predict(X)
check("fresh predictions finite and non-negative", np.isfinite(fresh).all() and (fresh >= 0).all())

saved = pd.read_csv(outdir / "final_test_predictions.csv").sort_values("id").reset_index(drop=True)
check("saved predictions: 28,248 unique test IDs", len(saved) == 28248 and saved.id.is_unique
      and set(saved.id) == set(test.id))
check("saved loss matches source", np.allclose(saved.loss.values, test.loss.values, atol=0, rtol=0))
max_diff = float(np.max(np.abs(saved.prediction.values - fresh)))
check("fresh vs saved predictions", max_diff < 1e-6, f"max |diff| = {max_diff:.3e}")

# 2. overall MAE recomputed from saved predictions
mae_saved = float(np.mean(np.abs(saved.loss - saved.prediction)))
mae_fresh = float(np.mean(np.abs(test.loss.values - fresh)))
receipt = json.loads((outdir / "final_test_evaluation_receipt.json").read_text())
check("test MAE (saved preds) matches receipt", abs(mae_saved - receipt["test_mae"]) < 1e-6, f"{mae_saved:.6f}")
check("test MAE (fresh preds) matches receipt", abs(mae_fresh - receipt["test_mae"]) < 1e-6, f"{mae_fresh:.6f}")

# 3. constant baselines on the same IDs (training-derived constants)
mean_c, med_c = train.loss.mean(), train.loss.median()
mae_mean = float(np.mean(np.abs(test.loss - mean_c)))
mae_med = float(np.mean(np.abs(test.loss - med_c)))
check("training mean constant", abs(mean_c - 3038.840254813309) < 1e-6, f"{mean_c:.4f}")
check("training median constant", abs(med_c - 2115.39) < 1e-9, f"{med_c:.2f}")
check("mean-constant test MAE matches receipt", abs(mae_mean - receipt["training_mean_constant_mae"]) < 1e-6, f"{mae_mean:.6f}")
check("median-constant test MAE matches receipt", abs(mae_med - receipt["training_median_constant_mae"]) < 1e-6, f"{mae_med:.6f}")
comp = pd.read_csv(outdir / "final_test_model_comparison.csv").set_index("model")
check("comparison CSV matches", abs(comp.loc["final_top75_catboost", "test_mae"] - mae_saved) < 1e-6
      and abs(comp.loc["training_mean_constant", "test_mae"] - mae_mean) < 1e-6
      and abs(comp.loc["training_median_constant", "test_mae"] - mae_med) < 1e-6)

# 4. segments from frozen training thresholds
thr = pd.read_csv(repo / "notebooks/final-deliverables/October/Gate 1/high_loss_support.csv")
p90 = thr.loc[thr.threshold == "train_p90", "threshold_value"].iloc[0]
p99 = thr.loc[thr.threshold == "train_p99", "threshold_value"].iloc[0]
seg = np.where(test.loss < p90, "below_p90", np.where(test.loss < p99, "p90_to_p99", "p99_and_above"))
check("saved segment labels match thresholds", (saved.loss_segment.values == seg).all())
tail = pd.read_csv(outdir / "final_test_tail_diagnostics.csv").set_index("loss_segment")
for s in ["below_p90", "p90_to_p99", "p99_and_above"]:
    m = seg == s
    n, mae = int(m.sum()), float(np.mean(np.abs(test.loss.values[m] - fresh[m])))
    check(f"segment {s}", n == tail.loc[s, "claims"] and abs(mae - tail.loc[s, "mae"]) < 1e-6,
          f"n={n} mae={mae:.2f} mean_loss={test.loss.values[m].mean():.2f} mean_pred={fresh[m].mean():.2f}")

print("\nSUMMARY:", sum(ok for _, ok, _ in results), "/", len(results), "checks passed")
print(f"test MAE {mae_saved:.2f} | mean {mae_mean:.2f} | median {mae_med:.2f} | "
      f"vs mean {100*(1-mae_saved/mae_mean):.2f}% | vs median {100*(1-mae_saved/mae_med):.2f}%")
