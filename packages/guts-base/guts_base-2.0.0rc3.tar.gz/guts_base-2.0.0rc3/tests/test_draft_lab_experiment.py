import pytest
import pandas as pd
from guts_base import PymobSimulator
from guts_base.data.generator import ExposureDataDict
from pymob.inference.scipy_backend import ScipyBackend
from guts_base.prob import conditional_survival
from guts_base.mod import RED_SD

def test_generate_single_exposure_lab_experiment_simulation(tmp_path):
    # This is the method to be developed for the WP2 task


    model = RED_SD()

    experiment = PymobSimulator.draft_laboratory_experiment(
        treatments={
            "control": 0.0, 
            "Treat 1": 1.0, 
            "Treat 2": 5.0, 
            "Treat 3": 50.0, 
            "Treat 4": 100.0,
        },
        survival_model=model,
        n_test_organisms_per_treatment=10,
        experiment_end=pd.Timedelta("10 days"),
        exposure_pattern=ExposureDataDict(start=0, end=None, exposure=None),
        exposure_interpolation="linear",
        dt=pd.Timedelta("1 day"),
    )


    experiment

    # TODO: [Opt] Results should be idata
    # TODO: Run with more config paramterized signature