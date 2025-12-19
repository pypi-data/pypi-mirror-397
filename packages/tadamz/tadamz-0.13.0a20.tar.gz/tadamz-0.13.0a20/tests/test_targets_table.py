# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 10:58:37 2023

@author: pkiefer
"""

import os
import pytest
import emzed
from emzed import RtType, MzType, Table
from src.tadamz import targets_table as tt

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config_srm():
    config = {
        "peak_search_window_size": 10.0,
        "subtract_baseline": True,
        "ms_data_type": "MS_Chromatogram",
    }
    return config


@pytest.fixture
def config_prm():
    config = {
        "integration_algorithm": "linear",
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "subtract_baseline": False,
        "ms_data_type": "Spectra",
        "peak_search_window_size": 10.0,
    }
    return config


@pytest.fixture
def config_ms1():
    config = {
        "precursor_mz_tol": None,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "subtract_baseline": False,
        "ms_data_type": "Spectra",
        "peak_search_window_size": 10.0,
    }
    return config


@pytest.fixture
def pt_srm():
    columns = (
        "precursor_mz",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "peak_search_window_min",
        "peak_search_window_max",
    )
    types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType]
    rows = [
        [
            372.212521,
            401.259831,
            401.159831,
            401.359831,
            165.77099609,
            None,
            None,
        ],
        [
            307.498975,
            404.198793,
            404.098793,
            404.298793,
            109.11599731,
            None,
            None,
        ],
        [
            408.550103,
            461.753824,
            461.653824,
            461.853824,
            133.89,
            133.89 - 5,
            133.89 + 5,
        ],
        [
            472.918238,
            552.286774,
            552.186774,
            552.386774,
            299.72,
            299.72 - 5,
            299.72 + 5,
        ],
    ]

    t = Table.create_table(columns, types, rows=rows)
    t.add_column_with_constant_value(
        "reduce_integration_window_to_peak_width", True, bool
    )
    return t


@pytest.fixture
def pt_prm():
    columns = (
        "precursor_mz",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "peak_search_window_min",
        "peak_search_window_max",
    )
    types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType]
    rows = [
        [
            146.0,
            102.05456351,
            102.05401611,
            102.05512238,
            269.702082,
            252.227826 - 5,
            287.866704 + 5,
        ],
        [
            215.0,
            89.0228633,
            89.02237701,
            89.02349091,
            83.833074,
            77.002614 - 5,
            89.731656 + 5,
        ],
        [
            146.0,
            128.03391296,
            128.03282166,
            128.03465271,
            270.865692,
            259.679022 - 5,
            287.866704 + 5,
        ],
        [
            215.0,
            179.05523453,
            179.05459595,
            179.05619812,
            83.522574,
            78.399984 - 5,
            88.645668 + 5,
        ],
    ]
    t = Table.create_table(columns, types, rows=rows)
    return t


@pytest.fixture
def pt_ms1():
    columns = (
        "mz",
        "mzmin",
        "mzmax",
        "rt",
    )
    types = [MzType, MzType, MzType, RtType]
    rows = [
        [175.11895, 175.11495, 175.12295, 332.4],
        [148.06043, 148.0564, 148.0644, 296.4],
        [134.0448, 134.0408, 134.0488, 316.2],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_column_with_constant_value(
        "reduce_integration_window_to_peak_width", True, bool
    )
    return t


@pytest.fixture
def pt_ms_prm():
    columns = (
        "precursor_mz",
        "mz",
        "rt",
        "peak_search_window_min",
        "peak_search_window_max",
    )
    types = [MzType, MzType, RtType, RtType, RtType]
    rows = [
        [None, 90.05495569, 259.2, 255 - 10, 262.8 + 10],
        [None, 94.06205569, 259.2, 255 - 10, 262.8 + 10],
        [175.1189529, 70.065669, 336, 332.4 - 5, 339.6 + 5],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_column_with_constant_value(
        "reduce_integration_window_to_peak_width", True, bool
    )
    return t


def test_setup_targets_table_0(pt_srm, config_srm):
    is_ = tt.setup_targets_table(pt_srm, config_srm)
    for lower, upper, rtmin, rtmax in zip(
        is_.peak_search_window_min,
        is_.peak_search_window_max,
        is_.rtmin_chromatogram,
        is_.rtmax_chromatogram,
    ):
        assert upper - lower - 10 == rtmax - rtmin - 10 < 1e-12


def test_setup_targets_table_1(pt_srm, config_srm):
    is_ = tt.setup_targets_table(pt_srm, config_srm).col_names
    expected = set(
        [
            "target_id",
            "precursor_mz_chromatogram",
            "mz_chromatogram",
            "rtmin_chromatogram",
            "rtmax_chromatogram",
            "subtract_baseline",
            "reduce_integration_window_to_peak_width",
        ]
    )
    assert expected - set(is_) == set()


def test_set_up_targets_table_2(pt_prm, config_prm):
    is_ = tt.setup_targets_table(pt_prm, config_prm).col_names
    expected = set(
        [
            "target_id",
            "precursor_mz",
            "mz",
            "rtmin",
            "rtmax",
            "subtract_baseline",
            "reduce_integration_window_to_peak_width",
        ]
    )
    assert expected - set(is_) == set()


def test_setup_targets_table_3(pt_ms1, config_ms1):
    is_ = tt.setup_targets_table(pt_ms1, config_ms1)
    for lower, upper, rtmin, rtmax in zip(
        is_.peak_search_window_min, is_.peak_search_window_max, is_.rtmin, is_.rtmax
    ):
        assert upper - lower - 10 == rtmax - rtmin - 10 < 1e-12


def test_setup_targets_table_4(pt_ms1, config_ms1):
    is_ = tt.setup_targets_table(pt_ms1, config_ms1).col_names
    expected = set(
        [
            "target_id",
            "precursor_mz",
            "mz",
            "rtmin",
            "rtmax",
            "peak_search_window_min",
            "peak_search_window_max",
            "subtract_baseline",
            "reduce_integration_window_to_peak_width",
        ]
    )
    assert expected - set(is_) == set()
