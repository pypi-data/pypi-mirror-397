# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:22:40 2023

@author: pkiefer
"""
import pytest
import emzed
import pickle
import os
import numpy as np
from emzed import MzType, RtType

# from src.targeted_wf import extract_peaks as ep
from src.tadamz import classify_peaks as cp
from src.tadamz.scoring import random_forest_peak_classification as rfc
from src.tadamz.extract_peaks import extract_peaks
from src.tadamz import in_out
from sklearn.ensemble import RandomForestClassifier

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def kwargs():
    kwargs = {
        "scoring_model": "random_forest_classification",
        "scoring_model_params": {
            "classifier_name": "test_peak_classifier",
            "path_to_folder": data_folder,
            "ms_data_type": "MS_Chromatogram",
        },
    }
    return kwargs


@pytest.fixture
def table():
    spath = os.path.join(here, "data", "classification_table_chromatogram.table")
    t = emzed.io.load_table(spath)
    return t


@pytest.fixture
def table1():
    spath = os.path.join(here, "data", "classification_table_ms1.table")
    t = emzed.io.load_table(spath)
    return t


@pytest.fixture
def kwargs1():
    kwargs = {
        "scoring_model": "random_forest_classification",
        "scoring_model_params": {
            "classifier_name": "uplc_MS1_QEx_peak_classifier",
            "ext": ".pickle",
            "path_to_folder": os.path.abspath(os.path.join(here, "data")),
        },
    }
    return kwargs


# @pytest.fixture
# def table2():
#     spath = os.path.join(here, "data", "score_table1.table")
#     t = emzed.io.load_table(spath)
#     return t


@pytest.fixture
def tm():
    columns = [
        "linear_model",
        "zigzag_index",
        "gaussian_similarity",
        "max_apex_boundery_ratio",
        "sharpness",
        "tpsar",
    ]
    rows = [[PModel(1e4), 3e40, 0, 1e-50, -2, -2e40]]
    types = [object, float, float, float, float, float]
    return emzed.Table.create_table(columns, types, rows=rows)


@pytest.fixture
def classifier():
    path = os.path.join(data_folder, "test_peak_classifier.pickle")
    with open(path, "rb") as fp:
        clf = pickle.load(fp)
    return clf


def test_classify_peaks_0(table, kwargs, regtest):
    t = cp.classify_peaks(table, kwargs)
    t = t.extract_columns("id", "peak_quality_score").to_pandas()
    print(t.to_string(), file=regtest)


def test_classify_peaks_1(table1, kwargs1, regtest):
    t = cp.classify_peaks(table1, kwargs1)
    t = t.extract_columns("id", "peak_quality_score").to_pandas()
    print(t.to_string(), file=regtest)


def test_score_peaks(table, classifier):
    cp.update_metrics(table)
    # handling scoring of empty arrays
    # we set the number of spectra to 1< min_specs (6)
    table.replace_column_with_constant_value("no_spectra", 1, int)
    cp.score_peaks(table, classifier)
    scores = set(table.peak_quality_score)
    assert len(scores) == 1 and scores.pop() == 0


def test__extract_classification_data(tm):
    data = rfc._extract_classification_data(tm)[0]
    expected = np.array([1e4, 1.0e38, 0, 0, -2, -1.0e38], dtype=np.float32)
    is_ = abs(data - expected)
    print(is_)
    print(data)
    print(expected)
    assert np.all(is_ < 1e-30)


def test_get_classifier_0():
    classifier_name = "test_peak_classifier"
    is_ = cp.get_classifier(classifier_name, data_folder)
    print(type(is_))
    assert isinstance(is_, RandomForestClassifier)


def test_get_classifier_1():
    classifier_name = "test_peak_classifier-rebuilt"
    before = in_out.load_classifier_object(classifier_name, ".json", data_folder)
    meta_data = {"sklearn": "5.0.6", "numpy": "1.26.3"}
    in_out.save_classifier_object(
        meta_data, classifier_name, ".json", data_folder, overwrite=True
    )
    _ = cp.get_classifier(classifier_name, data_folder)
    after = in_out.load_classifier_object(classifier_name, ".json", data_folder)
    print(after.keys())
    assert all(before[key] == after[key] for key in ["numpy", "sklearn"])


def test___evaluate_classifier_env_0(classifier):
    classifier_name = ""
    meta_data = {"sklearn": "5.0.6", "numpy": "1.26.3"}
    is_ = cp._evaluate_classifier_env(classifier, classifier_name, meta_data)
    assert is_ == False


def test___evaluate_classifier_env_1(classifier):
    classifier_name = ""
    meta_data = rfc._get_meta_data()
    is_ = cp._evaluate_classifier_env(classifier, classifier_name, meta_data)
    assert is_


# def test__evaluate_


class PModel:
    def __init__(self, area):
        self.area = area
