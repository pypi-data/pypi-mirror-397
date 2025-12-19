import pytest
import numpy as np

from guts_base import GutsBase
from guts_base.prob import conditional_survival
from pymob.inference.scipy_backend import ScipyBackend

from tests.conftest import (
    OPENGUTS_ESTIMATES,
)


def assert_convergence(sim: GutsBase, rtol=0.05, atol=0.1):
    # test if inferer converged on the true estmiates
    pymob_estimates = sim.inferer.idata.posterior.median(("chain", "draw"))
    pymob_estimates_array = pymob_estimates.to_array().sortby("variable")
    openguts_estimates = OPENGUTS_ESTIMATES[sim._model_class.__name__.lower()]
    

    if openguts_estimates is None:
        # this explicitly skips testing the results, since they are not available,
        # but does not fail the test.
        pytest.skip()

    openguts_estimates = openguts_estimates[list(pymob_estimates.data_vars)]
    openguts_estimates_array = openguts_estimates.to_array().sortby("variable")
    np.testing.assert_allclose(
        pymob_estimates_array, 
        openguts_estimates_array, 
        rtol=rtol, atol=atol
    )



# run tests with the Simulation fixtures
def test_setup(sim: GutsBase):
    """Tests the construction method"""
    assert True


def test_simulation(sim: GutsBase):
    """Tests if a forward simulation pass can be computed"""
    # sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True

@pytest.mark.slow
def test_likelihood(sim: GutsBase):
    # TODO: fix this test. As long as probabilities are not too extreme, scipy and 
    # numpyro return the same solutions. I need to investigate why this breaks down
    # at some point. Simple fixes are nans (numpyro returns zeros for true nans, and
    # nans in survivors are forward filled (maybe this is also part of the solution?))
    # It works for RED_SD and RED_IT possibly, because the default parameters work better
    # for the problem. I need to put the computations side by side and investigate 
    # parameters and check where things depart. 
    pytest.skip()

    # set up numpyro backend
    sim.config.inference_numpyro.gaussian_base_distribution = False
    sim.set_inferer("numpyro")

    # create a likelihood function from the probability model
    loglik, _ = sim.inferer.create_log_likelihood(check=False, gradients=False, seed=1, return_type="full", scaled=False) # type: ignore

    # calculate the probabilities of piror and observations with numpyro
    theta = sim.model_parameter_dict
    ll = loglik(theta=theta)
    log_likelihood_observations_numpyro = ll[2]["survival_obs"]
    # log_likelihood_prior_numpyro = xr.Dataset(data_vars=ll[1]).to_array().values


    # Set up the scipy backend
    # TODO: Eventually improve that API so it is more user friendly
    conditional_survival.eps = float(sim.observations.eps.values)
    ScipyBackend._distribution.distribution_map["conditional_survival"] = (conditional_survival, {})
    
    # set the initial number
    sim.config.error_model.survival =\
        "conditional_survival(p=survival,n=survivors_at_start[:,[0]])"

    # set up scipy backend    
    sim.set_inferer("scipy")
    
    # calculate the probabilities of piror and observations with scipy
    results = sim.inferer.inference_model(theta=theta, observations=sim.observations)
    log_likelihood_observations_scipy = results["observations_prob"]["survival"]

    # test if likelihood computations are comparable
    np.testing.assert_almost_equal(
        log_likelihood_observations_scipy, 
        log_likelihood_observations_numpyro
    )



    results["theta_prob"]

    # TODO Compare vincents' LP calculations


@pytest.mark.slow
def test_export_import_sim(sim: GutsBase):
    sim.export()
    sim_export_results = sim.evaluate()
    imported_sim = GutsBase.from_directory(directory=sim.output_path)

    # just try accessing the posterior object
    sim_import_results = imported_sim.evaluate()

    # assert that the results from both simulations are exactly identical
    diff = sim_export_results - sim_import_results
    np.testing.assert_array_equal(diff.sum().to_array().values, 0)



@pytest.mark.integration
@pytest.mark.batch1
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference(sim: GutsBase, backend):
    # test inference with default settings
    sim.set_inferer(backend)
    sim.prior_predictive_checks()
    sim.inferer.run()
    sim.export()
    sim.posterior_predictive_checks()

    # Test report generation with reduced extent
    # for ECx computation (this can take a long time)
    sim.config.guts_base.ecx_mode = "draws"
    sim.config.guts_base.ecx_draws = 3
    sim.config.guts_base.ecx_force_draws = True
    sim.config.guts_base.ecx_estimates_x = [0.5]
    sim.config.guts_base.ecx_estimates_times = [2]
    sim.config.report.debug_report = True
    sim.report()

    assert_convergence(sim, rtol=0.05, atol=0.1)


@pytest.mark.integration
@pytest.mark.batch2
def test_estimate_parameters_separate_control_mortality(sim: GutsBase):
    sim.config.report.debug_report = True

    sim.estimate_parameters(
        forward_interpolate_exposure_data=True,
        background_mortality="pre-fit"
    )
    assert_convergence(sim, rtol=0.1, atol=0.1)


@pytest.mark.integration
@pytest.mark.batch3
def test_estimate_parameters_separate_control_mortality_transform_nuts(sim: GutsBase):
    max_exposure = float(sim.observations.exposure.max().values)
    sim.config.report.debug_report = True

    sim.estimate_parameters(
        forward_interpolate_exposure_data=True,
        transform_scalings={"x_in_factor": max_exposure, "time_factor": 1.0},
        background_mortality="pre-fit",
        inference_numpyro_kernel="nuts",
        inference_numpyro_nuts_warmup=1000,
        inference_numpyro_draws=500,
        inference_numpyro_nuts_chains=1,
    )
    assert_convergence(sim, rtol=0.1, atol=0.1)

@pytest.mark.integration
@pytest.mark.batch4
def test_estimate_parameters_nuts(sim: GutsBase):
    sim.config.report.debug_report = True
    sim.estimate_parameters(
        forward_interpolate_exposure_data=True,
        inference_numpyro_kernel="nuts",
        inference_numpyro_nuts_warmup=1000,
        inference_numpyro_draws=500,
        inference_numpyro_nuts_chains=1,
    )
    assert_convergence(sim, rtol=0.1, atol=0.1)
