import os
from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest
from inicheck.tools import MasterConfig, cast_all_variables, get_user_config

import pysnobal
from pysnobal.pysnobal import PySnobal

BASE_INI_FILE_NAME = 'pysnobal_config.ini'
test_dir = Path(pysnobal.__file__).parent.joinpath('tests')
config_file = os.path.join(test_dir, BASE_INI_FILE_NAME)


@pytest.fixture(scope='module')
def base_config():
    """Load the base config object"""

    master_config = os.path.join(
        Path(pysnobal.__file__).parent, 'pysnobal_core_config.ini')
    mcfg = MasterConfig(path=master_config)
    return get_user_config(config_file, mcfg=mcfg)


@pytest.fixture
def base_config_copy(base_config):
    """Create a copy of the base config object"""
    return deepcopy(base_config)


@pytest.fixture(autouse=True)
def make_clean():
    """Make the directory and clean up after the test"""

    os.makedirs('pysnobal/tests/output', exist_ok=True)
    yield
    os.remove('pysnobal/tests/output/pysnobal_output.csv')


def test_pysnobal_output_normal(make_clean, base_config):

    # run PySnobal
    status = PySnobal(base_config).run()
    assert status

    # load in the outputs
    gold = pd.read_csv(
        'pysnobal/tests/test_data_point/gold_csv/gold.pysnobal.csv',
        index_col='date_time', parse_dates=True)
    gold.index = gold.index.tz_convert('MST')

    new = pd.read_csv(
        'pysnobal/tests/output/pysnobal_output.csv',
        index_col='date_time', parse_dates=True)
    new.index = new.index.tz_convert('MST')

    pd.testing.assert_frame_equal(gold, new)


def test_pysnobal_ouput_all(make_clean, base_config_copy):

    config = base_config_copy
    config.raw_cfg['files'].update({'output_mode': 'all'})

    config.apply_recipes()
    config = cast_all_variables(config, config.mcfg)

    # run PySnobal
    status = PySnobal(config).run()
    assert status

    # load in the outputs
    gold = pd.read_csv(
        'pysnobal/tests/test_data_point/gold_csv/gold.pysnobal.all.csv',
        index_col='date_time', parse_dates=True)
    gold.index = gold.index.tz_convert('MST')

    new = pd.read_csv(
        'pysnobal/tests/output/pysnobal_output.csv',
        index_col='date_time', parse_dates=True)
    new.index = new.index.tz_convert('MST')

    pd.testing.assert_frame_equal(gold, new)
