from typing import List

import numpy as np
from matplotlib.figure import Figure

from statista.distributions import GEV, ConfidenceInterval, Gumbel, PlottingPosition


def test_plotting_position_weibul(
        time_series1: list,
):
    cdf = PlottingPosition.Weibul(time_series1, option=1)
    assert isinstance(cdf, np.ndarray)
    rp = PlottingPosition.Weibul(time_series1, option=2)
    assert isinstance(rp, np.ndarray)

def test_plotting_position_rp(
        time_series1: list,
):
    cdf = PlottingPosition.Weibul(time_series1, option=1)
    rp = PlottingPosition.Returnperiod(cdf)
    assert isinstance(rp, np.ndarray)


def test_create_gumbel_instance(
        time_series1: list,
):
    Gdist = Gumbel(time_series1)
    assert isinstance(Gdist.data, np.ndarray)
    assert isinstance(Gdist.data_sorted, np.ndarray)


def test_gumbel_estimate_parameter(
        time_series2: list,
        dist_estimation_parameters: List[str],
):
    Gdist = Gumbel(time_series2)
    for i in range(len(dist_estimation_parameters)):
        param = Gdist.EstimateParameter(method=dist_estimation_parameters[i], Test=False)
        assert isinstance(param, list)
        assert Gdist.loc
        assert Gdist.scale


def test_parameter_estimation_optimization(
        time_series2: list,
        dist_estimation_parameters: List[str],
        parameter_estimation_optimization_threshold: int,
):
    Gdist = Gumbel(time_series2)
    param = Gdist.EstimateParameter(
        method="optimization", ObjFunc=Gumbel.ObjectiveFn,
        threshold=parameter_estimation_optimization_threshold
    )
    assert isinstance(param, list)
    assert Gdist.loc
    assert Gdist.scale

def test_gumbel_ks(
        time_series2: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = Gumbel(time_series2)
    Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Gdist.ks()
    assert Gdist.Dstatic
    assert Gdist.KS_Pvalue



def test_gumbel_chisquare(
        time_series2: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = Gumbel(time_series2)
    Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Gdist.chisquare()
    assert Gdist.chistatic
    assert Gdist.chi_Pvalue


def test_gumbel_pdf(
        time_series2: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = Gumbel(time_series2)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    pdf, fig, ax = Gdist.pdf(Param[0], Param[1], plot_figure=True)
    assert isinstance(pdf, np.ndarray)
    assert isinstance(fig, Figure)


def test_gumbel_cdf(
        time_series2: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = Gumbel(time_series2)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    cdf, fig, ax = Gdist.cdf(Param[0], Param[1], plot_figure=True)
    assert isinstance(cdf, np.ndarray)
    assert isinstance(fig, Figure)


def test_gumbel_TheporeticalEstimate(
        time_series2: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = Gumbel(time_series2)
    cdf_Weibul = PlottingPosition.Weibul(time_series2)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Qth = Gdist.TheporeticalEstimate(Param[0], Param[1], cdf_Weibul)
    assert isinstance(Qth, np.ndarray)


def test_gumbel_confidence_interval(
        time_series2: list,
        dist_estimation_parameters_ks: str,
        confidence_interval_alpha: float
):
    Gdist = Gumbel(time_series2)
    cdf_Weibul = PlottingPosition.Weibul(time_series2)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    upper, lower = Gdist.ConfidenceInterval(Param[0], Param[1], cdf_Weibul, alpha=confidence_interval_alpha)
    assert isinstance(upper, np.ndarray)
    assert isinstance(lower, np.ndarray)


def test_gumbel_probapility_plot(
        time_series2: list,
        dist_estimation_parameters_ks: str,
        confidence_interval_alpha: float
):
    Gdist = Gumbel(time_series2)
    cdf_Weibul = PlottingPosition.Weibul(time_series2)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    [fig1, fig2], [ax1, ax2] = Gdist.ProbapilityPlot(Param[0], Param[1], cdf_Weibul, alpha=confidence_interval_alpha)
    assert isinstance(fig1, Figure)
    assert isinstance(fig2, Figure)





def test_create_gev_instance(
        time_series1: list,
):
    Gdist = GEV(time_series1)
    assert isinstance(Gdist.data, np.ndarray)
    assert isinstance(Gdist.data_sorted, np.ndarray)


def test_gev_estimate_parameter(
        time_series1: list,
        dist_estimation_parameters: List[str],
):
    Gdist = GEV(time_series1)
    for i in range(len(dist_estimation_parameters)):
        param = Gdist.EstimateParameter(method=dist_estimation_parameters[i], Test=False)
        assert isinstance(param, list)
        assert Gdist.loc
        assert Gdist.scale
        assert Gdist.shape


def test_gev_ks(
        time_series1: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = GEV(time_series1)
    Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Gdist.ks()
    assert Gdist.Dstatic
    assert Gdist.KS_Pvalue

def test_gev_chisquare(
        time_series1: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = GEV(time_series1)
    Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Gdist.chisquare()
    assert Gdist.chistatic
    assert Gdist.chi_Pvalue


def test_gev_pdf(
        time_series1: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = GEV(time_series1)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    pdf, fig, ax = Gdist.pdf(Param[0], Param[1], Param[2], plot_figure=True)
    assert isinstance(pdf, np.ndarray)
    assert isinstance(fig, Figure)


def test_gev_cdf(
        time_series1: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = GEV(time_series1)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    cdf, fig, ax = Gdist.cdf(Param[0], Param[1], Param[2], plot_figure=True)
    assert isinstance(cdf, np.ndarray)
    assert isinstance(fig, Figure)

def test_gev_TheporeticalEstimate(
        time_series1: list,
        dist_estimation_parameters_ks: str,
):
    Gdist = GEV(time_series1)
    cdf_Weibul = PlottingPosition.Weibul(time_series1)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    Qth = Gdist.TheporeticalEstimate(Param[0], Param[1], Param[2],cdf_Weibul)
    assert isinstance(Qth, np.ndarray)


def test_gev_confidence_interval(
        time_series1: list,
        dist_estimation_parameters_ks: str,
        confidence_interval_alpha: float
):
    Gdist = GEV(time_series1)
    cdf_Weibul = PlottingPosition.Weibul(time_series1)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    func = ConfidenceInterval.GEVfunc
    upper, lower = Gdist.ConfidenceInterval(
        Param[0], Param[1], Param[2], F=cdf_Weibul, alpha=confidence_interval_alpha,
        statfunction=func, n_samples=len(time_series1)
    )
    assert isinstance(upper, np.ndarray)
    assert isinstance(lower, np.ndarray)


def test_confidence_interval_directly(
        time_series1: list,
        dist_estimation_parameters_ks: str,
        confidence_interval_alpha: float
):
    Gdist = GEV(time_series1)
    cdf_Weibul = PlottingPosition.Weibul(time_series1)
    Param = Gdist.EstimateParameter(method=dist_estimation_parameters_ks, Test=False)
    func = ConfidenceInterval.GEVfunc
    # upper, lower = Gdist.ConfidenceInterval(
    #     Param[0], Param[1], Param[2], F=cdf_Weibul, alpha=confidence_interval_alpha,
    #     statfunction=func, n_samples=len(time_series1)
    # )
    CI = ConfidenceInterval.BootStrap(
        time_series1, statfunction=func, gevfit=Param, n_samples=len(time_series1), F=cdf_Weibul
    )
    LB = CI["LB"]
    UB = CI["UB"]

    assert isinstance(LB, np.ndarray)
    assert isinstance(UB, np.ndarray)
