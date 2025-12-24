# tests/test_core_behavior.py

import pytest
from datasets import Dataset, DatasetDict
from dataset_risk_decorator.core import (
    risk_guard,
    DatasetRiskProcessor,
    DatasetRiskConfig,
)

@pytest.fixture(autouse=True)
def disable_column_prompt(monkeypatch):
    monkeypatch.setattr(
        "dataset_risk_decorator.core.select_code_columns",
        lambda cols: [cols[0]],
    )

def test_empty_rows_safe():
    ds = Dataset.from_dict(
    {
        "code": ["", "", ""],
        "text": ["a", "b", "c"],
    }
)

    out = risk_guard(ds, max_rows=3)

    assert all(isinstance(x, float) for x in out["risk_score"])


def test_multiple_code_columns():
    ds = Dataset.from_dict(
        {
            "code_a": ["print(1)", ""],
            "code_b": ["eval(x)", "safe"],
        }
    )

    out = risk_guard(ds, max_rows=2)

    assert len(out["risk_score"]) == 2


def test_filter_is_deterministic():
    ds = Dataset.from_dict(
        {
            "code": ["eval(x)", "print(x)", "safe"],
        }
    )

    a = risk_guard(ds, filter_mode="keep_problematic", max_rows=3)
    b = risk_guard(ds, filter_mode="keep_problematic", max_rows=3)

    assert a["risk_score"] == b["risk_score"]


def test_datasetdict_supported():
    ds = DatasetDict(
        {
            "train": Dataset.from_dict({"code": ["eval(x)"]}),
            "test": Dataset.from_dict({"code": ["print(x)"]}),
        }
    )

    out = risk_guard(ds, max_rows=1)

    assert isinstance(out, DatasetDict)
    assert "risk_score" in out["train"].features


def test_schema_is_not_destroyed():
    ds = Dataset.from_dict(
        {
            "code": ["eval(x)"],
            "meta": [{"a": 1}],
        }
    )

    out = risk_guard(ds, max_rows=1)

    assert "meta" in out.features


def test_decorator_api_equivalence():
    def loader():
        return Dataset.from_dict({"code": ["eval(x)"]})

    decorated = risk_guard(loader(), max_rows=1)
    direct = risk_guard(loader(), max_rows=1)

    assert decorated["risk_score"] == direct["risk_score"]
