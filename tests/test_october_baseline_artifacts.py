import hashlib
import json
import math
import re
import statistics
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE1 = ROOT / "notebooks/final-deliverables/October/Gate 1"
GATE2 = ROOT / "notebooks/final-deliverables/October/Gate 2"
SOURCE_PATH = ROOT / "data/allstate_claims_data.csv"
MANIFEST_PATH = GATE1 / "partition_manifest.csv"
RUN_MANIFEST_PATH = GATE1 / "modeling_run_manifest.json"
NOTEBOOK_PATH = GATE2 / "constant_baselines.ipynb"
RESULTS_PATH = GATE2 / "baseline_results.csv"
PREDICTIONS_PATH = GATE2 / "baseline_predictions.csv"
CHECKS_PATH = GATE2 / "baseline_checks.csv"
RECEIPT_PATH = GATE2 / "baseline_run_receipt.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code_cells(notebook):
    return ["".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"]


# recomputes both baselines with plain Python, separately from the notebook's pandas/sklearn path
class IndependentRecalculationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = pd.read_csv(SOURCE_PATH, usecols=["id", "loss"])
        manifest = pd.read_csv(MANIFEST_PATH, usecols=["id", "partition"])
        partition_of = dict(zip(manifest["id"], manifest["partition"]))
        cls.train_loss = [float(loss) for i, loss in zip(source["id"], source["loss"])
                          if partition_of[i] == "train"]
        cls.validation_loss = [float(loss) for i, loss in zip(source["id"], source["loss"])
                               if partition_of[i] == "validation"]
        cls.results = pd.read_csv(RESULTS_PATH).set_index("model")

    def independent_mae(self, constant):
        return math.fsum(abs(loss - constant) for loss in self.validation_loss) / len(self.validation_loss)

    def test_results_list_mean_baseline_then_median_comparator(self):
        self.assertEqual(list(self.results.index), ["training_mean_constant", "training_median_constant"])
        self.assertEqual(list(self.results["role"]), ["required baseline", "comparator"])
        self.assertEqual(set(self.results["fitted_on"]), {"train"})
        self.assertEqual(set(self.results["evaluated_on"]), {"validation"})

    def test_constants_are_training_mean_and_median(self):
        mean = math.fsum(self.train_loss) / len(self.train_loss)
        median = statistics.median(self.train_loss)
        self.assertAlmostEqual(self.results.loc["training_mean_constant", "fitted_constant"], mean, places=6)
        self.assertAlmostEqual(self.results.loc["training_median_constant", "fitted_constant"], median, places=6)

    def test_claim_counts(self):
        self.assertEqual(len(self.train_loss), 131822)
        self.assertEqual(set(self.results["train_claims"]), {131822})
        self.assertEqual(set(self.results["validation_claims"]), {len(self.validation_loss)})

    def test_validation_mae_matches_independent_calculation(self):
        for model, row in self.results.iterrows():
            with self.subTest(model=model):
                expected = self.independent_mae(row["fitted_constant"])
                self.assertAlmostEqual(row["validation_mae"], expected, places=6)

class BaselinePredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predictions = pd.read_csv(PREDICTIONS_PATH)
        cls.manifest = pd.read_csv(MANIFEST_PATH)

        cls.validation_ids = set(
            cls.manifest.loc[
                cls.manifest["partition"] == "validation",
                "id",
            ]
        )

    def test_one_prediction_per_validation_claim(self):
        self.assertEqual(len(self.predictions), 28248)
        self.assertTrue(self.predictions["id"].is_unique)
        self.assertEqual(set(self.predictions["id"]), self.validation_ids)

    def test_prediction_columns(self):
        self.assertEqual(
            list(self.predictions.columns),
            [
                "id",
                "training_mean_constant",
                "training_median_constant",
            ],
        )

    def test_predictions_are_finite(self):
        for column in [
            "training_mean_constant",
            "training_median_constant",
        ]:
            self.assertTrue(
                self.predictions[column].map(math.isfinite).all()
            )

    def test_prediction_values_match_saved_constants(self):
        results = pd.read_csv(RESULTS_PATH).set_index("model")

        self.assertTrue(
            (
                self.predictions["training_mean_constant"]
                == results.loc["training_mean_constant", "fitted_constant"]
            ).all()
        )

        self.assertTrue(
            (
                self.predictions["training_median_constant"]
                == results.loc["training_median_constant", "fitted_constant"]
            ).all()
        )

class BaselineChecksTests(unittest.TestCase):
    def test_all_checks_pass(self):
        checks = pd.read_csv(CHECKS_PATH)
        self.assertEqual(sorted(checks["check_id"]), ["B1", "B2", "B3", "B4", "B5", "B6", "B7"])
        self.assertTrue((checks["status"] == "pass").all(), checks.to_string())


class RunReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        cls.split = json.loads(RUN_MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    def test_run_id_format(self):
        self.assertRegex(self.receipt["run_id"], r"^OCT-BASE-\d{8}T\d{6}Z-[0-9a-f]{8}$")

    def test_receipt_names_the_frozen_split_and_source(self):
        self.assertEqual(self.receipt["split_version"], self.split["split"]["version"])
        self.assertEqual(self.receipt["modeling_data_version"], self.split["modeling_data_version"])
        self.assertEqual(self.receipt["manifest_sha256"], sha256(MANIFEST_PATH))
        self.assertEqual(self.receipt["source_sha256"], sha256(SOURCE_PATH))

    # editing the notebook without rerunning it leaves a receipt for different code
    def test_receipt_matches_current_notebook_code(self):
        code = "\n\n".join(code_cells(self.notebook))
        self.assertEqual(self.receipt["notebook_code_sha256"], hashlib.sha256(code.encode("utf-8")).hexdigest())

    def test_receipt_results_match_results_file(self):
        results = pd.read_csv(RESULTS_PATH).to_dict(orient="records")

        self.assertEqual(len(self.receipt["results"]), len(results))

        for receipt_row, csv_row in zip(self.receipt["results"], results):
            self.assertEqual(receipt_row["model"], csv_row["model"])
            self.assertEqual(receipt_row["role"], csv_row["role"])
            self.assertEqual(receipt_row["fitted_on"], csv_row["fitted_on"])
            self.assertEqual(receipt_row["evaluated_on"], csv_row["evaluated_on"])
            self.assertEqual(receipt_row["train_claims"], csv_row["train_claims"])
            self.assertEqual(receipt_row["validation_claims"], csv_row["validation_claims"])

            self.assertAlmostEqual(
                receipt_row["fitted_constant"],
                csv_row["fitted_constant"],
                places=6,
            )

            self.assertAlmostEqual(
                receipt_row["validation_mae"],
                csv_row["validation_mae"],
                places=6,
            )

    def test_library_versions_are_recorded(self):
        for library in ["python", "scikit-learn", "pandas", "numpy"]:
            self.assertIn(library, self.receipt["library_versions"])


class NotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        cls.code = code_cells(cls.notebook)

    def test_notebook_ran_top_to_bottom(self):
        counts = [cell.get("execution_count") for cell in self.notebook["cells"] if cell["cell_type"] == "code"]
        self.assertEqual(counts, list(range(1, len(counts) + 1)))

    # October leaves test-partition targets unexamined; loss is joined only after test rows are dropped
    def test_test_partition_rows_are_dropped_before_loss_is_used(self):
        source = "\n".join(self.code)
        drop = source.index('isin(["train", "validation"])')
        first_loss_use = min(m.start() for m in re.finditer(r'\["loss"\]', source))
        self.assertLess(drop, first_loss_use)

    def test_colab_users_can_set_root_by_hand(self):
        self.assertTrue(any("ROOT_OVERRIDE = None" in source for source in self.code))


if __name__ == "__main__":
    unittest.main()
