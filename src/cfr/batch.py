"""Utilities for running commands in batches."""

import numpy as np
import click
from cfr import framework


def expand_variants(fcf_features, ff_features, sublayer_param, fixed_param):
    """Expand variant lists to make full specifications."""
    fcf_list = fcf_features.split(',')
    ff_list = ff_features.split(',')
    if sublayer_param is not None:
        sub_list = sublayer_param.split(',')
    else:
        sub_list = []
    if fixed_param is not None:
        fix_list = fixed_param.split(',')
    else:
        fix_list = []

    max_n = np.max([len(arg) for arg in [fcf_list, ff_list, sub_list, fix_list]])
    if len(fcf_list) == 1:
        fcf_list *= max_n
    if len(ff_list) == 1:
        ff_list *= max_n
    if sublayer_param is not None:
        if len(sub_list) == 1:
            sub_list *= max_n
    else:
        sub_list = [None] * max_n
    if fixed_param is not None:
        if len(fix_list) == 1:
            fix_list *= max_n
    else:
        fix_list = [None] * max_n
    return fcf_list, ff_list, sub_list, fix_list


def command_fit_cmr(
    study,
    fit,
    fcf_features,
    ff_features,
    sublayers,
    subpar,
    fixed,
    n_reps=10,
    n_jobs=48,
    tol=0.00001,
    n_sim_reps=50,
):
    """Generate command line arguments for fitting CMR."""
    study_dir, data_file, patterns_file = framework.get_study_paths(study)
    inputs = f'{data_file} {patterns_file}'
    res_name = framework.generate_model_name(
        fcf_features, ff_features, sublayers, subpar, fixed
    )
    opts = f'-t {tol:.6f} -n {n_reps} -j {n_jobs} -r {n_sim_reps}'

    if sublayers:
        opts = f'--sublayers {opts}'
    else:
        opts = f'--no-sublayers {opts}'

    if subpar:
        opts += f' -p {subpar}'
    if fixed:
        opts += f' -f {fixed}'
    full_dir = study_dir / study / 'fits' / fit / res_name

    print(f'cfr-fit-cmr {inputs} {fcf_features} {ff_features} {full_dir} {opts}')


@click.command()
@click.argument("study")
@click.argument("fit")
@click.argument("fcf_features")
@click.argument("ff_features")
@click.option("--sublayers/--no-sublayers", default=False)
@click.option(
    "--sublayer-param",
    "-p",
    help="parameters free to vary between sublayers (e.g., B_enc-B_rec)",
)
@click.option(
    "--fixed-param",
    "-f",
    help="dash-separated list of values for fixed parameters (e.g., B_enc_cat=1)",
)
@click.option(
    "--n-reps",
    "-n",
    type=int,
    default=1,
    help="number of times to replicate the search",
)
@click.option(
    "--n-jobs", "-j", type=int, default=1, help="number of parallel jobs to use"
)
@click.option("--tol", "-t", type=float, default=0.00001, help="search tolerance")
@click.option(
    "--n-sim-reps",
    "-r",
    type=int,
    default=1,
    help="number of experiment replications to simulate",
)
def plan_fit_cmr(
    study,
    fit,
    fcf_features,
    ff_features,
    sublayers,
    sublayer_param,
    fixed_param,
    **kwargs,
):
    """Print command lines for fitting multiple models."""
    fcf_list, ff_list, sub_list, fix_list = expand_variants(
        fcf_features, ff_features, sublayer_param, fixed_param
    )
    for fcf, ff, sub, fix in zip(fcf_list, ff_list, sub_list, fix_list):
        command_fit_cmr(
            study,
            fit,
            fcf,
            ff,
            sublayers,
            sub,
            fix,
            **kwargs,
        )


def command_xval_cmr(
    study,
    fit,
    fcf_features,
    ff_features,
    sublayers,
    subpar,
    fixed,
    n_folds=None,
    fold_key=None,
    n_reps=10,
    n_jobs=48,
    tol=0.00001,
):
    """Generate command line arguments for fitting CMR."""
    study_dir, data_file, patterns_file = framework.get_study_paths(study)
    inputs = f'{data_file} {patterns_file}'
    res_name = framework.generate_model_name(
        fcf_features, ff_features, sublayers, subpar, fixed
    )
    opts = f'-t {tol:.6f} -n {n_reps} -j {n_jobs}'
    if n_folds is not None:
        opts += f' -d {n_folds}'
    if fold_key is not None:
        opts += f' -k {fold_key}'

    if sublayers:
        opts = f'--sublayers {opts}'
    else:
        opts = f'--no-sublayers {opts}'

    if subpar:
        opts += f' -p {subpar}'
    if fixed:
        opts += f' -f {fixed}'
    full_dir = study_dir / study / 'fits' / fit / res_name

    print(f'cfr-xval-cmr {inputs} {fcf_features} {ff_features} {full_dir} {opts}')


@click.command()
@click.argument("study")
@click.argument("fit")
@click.argument("fcf_features")
@click.argument("ff_features")
@click.option("--sublayers/--no-sublayers", default=False)
@click.option(
    "--sublayer-param",
    "-p",
    help="parameters free to vary between sublayers (e.g., B_enc-B_rec)",
)
@click.option(
    "--fixed-param",
    "-f",
    help="dash-separated list of values for fixed parameters (e.g., B_enc_cat=1)",
)
@click.option(
    "--n-folds",
    "-d",
    type=int,
    help="number of cross-validation folds to run",
)
@click.option(
    "--fold-key",
    "-k",
    help="events column to use when defining cross-validation folds",
)
@click.option(
    "--n-reps",
    "-n",
    type=int,
    default=1,
    help="number of times to replicate the search",
)
@click.option(
    "--n-jobs", "-j", type=int, default=1, help="number of parallel jobs to use"
)
@click.option("--tol", "-t", type=float, default=0.00001, help="search tolerance")
def plan_xval_cmr(
    study,
    fit,
    fcf_features,
    ff_features,
    sublayers,
    sublayer_param,
    fixed_param,
    **kwargs,
):
    """Print command lines for fitting multiple models."""
    fcf_list, ff_list, sub_list, fix_list = expand_variants(
        fcf_features, ff_features, sublayer_param, fixed_param
    )
    for fcf, ff, sub, fix in zip(fcf_list, ff_list, sub_list, fix_list):
        command_xval_cmr(
            study,
            fit,
            fcf,
            ff,
            sublayers,
            sub,
            fix,
            **kwargs,
        )


def command_sim_cmr(study, fit, model, n_rep=1):
    """Generate command line arguments for simulating CMR."""
    study_dir, data_file, patterns_file = framework.get_study_paths(study)
    fit_dir = study_dir / study / 'fits' / fit / model
    if not fit_dir.exists():
        raise IOError(f'Fit directory does not exist: {fit_dir}')
    print(f'cfr-sim-cmr {data_file} {patterns_file} {fit_dir} -r {n_rep}')


@click.command()
@click.argument("study")
@click.argument("fit")
@click.argument("models")
@click.option(
    "--n-sim-reps",
    "-r",
    type=int,
    default=1,
    help="number of experiment replications to simulate",
)
def plan_sim_cmr(study, fit, models, n_sim_reps):
    """Print command lines for simulating multiple models."""
    for model in models.split(","):
        command_sim_cmr(study, fit, model, n_sim_reps)
