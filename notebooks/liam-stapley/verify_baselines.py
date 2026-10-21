import pandas as pd

DATA = "data/allstate_claims_data.csv"
MANIFEST = "notebooks/final-deliverables/October/Gate 1/partition_manifest.csv"

data = pd.read_csv(DATA, usecols=["id", "loss"])
manifest = pd.read_csv(MANIFEST, usecols=["id", "partition"])

df = data.merge(
    manifest,
    on="id",
    how="inner",
    validate="one_to_one",
)

train = df[df["partition"] == "train"].copy()
validation = df[df["partition"] == "validation"].copy()

assert len(train) == 131_822
assert len(validation) == 28_248

mean_constant = train["loss"].mean()
median_constant = train["loss"].median()

mean_mae = (validation["loss"] - mean_constant).abs().mean()
median_mae = (validation["loss"] - median_constant).abs().mean()

print(f"train claims: {len(train)}")
print(f"validation claims: {len(validation)}")
print(f"training mean constant: {mean_constant:.12f}")
print(f"training median constant: {median_constant:.12f}")
print(f"mean baseline MAE: {mean_mae:.12f}")
print(f"median baseline MAE: {median_mae:.12f}")

predictions = pd.read_csv(
    "notebooks/final-deliverables/October/Gate 2/baseline_predictions.csv"
)

validation_ids = set(validation["id"])

assert len(predictions) == 28_248
assert predictions["id"].is_unique
assert set(predictions["id"]) == validation_ids
assert predictions["training_mean_constant"].notna().all()
assert predictions["training_median_constant"].notna().all()

print("baseline_predictions.csv verification passed.")