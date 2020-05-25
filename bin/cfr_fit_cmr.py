#!/usr/bin/env python
#
# Fit CMR to CFR data.

import os
import argparse
import pandas as pd
from cymr import models
from cymr import network
from cymr import fit
from cfr import framework


def main(data_file, patterns_file, fcf_features, ff_features, res_dir,
         n_reps=1, n_jobs=1, tol=0.00001):

    # run individual parameter search
    data = pd.read_csv(data_file)
    model = models.CMRDistributed()
    wp = framework.model_variant(fcf_features, ff_features)
    patterns = network.load_patterns(patterns_file)
    results = model.fit_indiv(data, wp.fixed, wp.free, wp.dependent,
                              patterns=patterns, weights=wp.weights,
                              n_jobs=n_jobs, method='de', n_rep=n_reps,
                              tol=tol)

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    # full search information
    res_file = os.path.join(res_dir, 'search.csv')
    results.to_csv(res_file)
    json_file = os.path.join(res_dir, 'parameters.json')
    wp.to_json(json_file)

    # best results
    best = fit.get_best_results(results)
    best_file = os.path.join(res_dir, 'fit.csv')
    best.to_csv(best_file)

    # simulate data based on best parameters
    subj_param = best.T.to_dict()
    study_data = data.loc[(data['trial_type'] == 'study')]
    sim = model.generate(study_data, {}, subj_param,
                         patterns=patterns, weights=wp.weights)
    sim_file = os.path.join(res_dir, 'sim.csv')
    sim.to_csv(sim_file, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file')
    parser.add_argument('patterns_file')
    parser.add_argument('fcf_features')
    parser.add_argument('ff_features')
    parser.add_argument('res_dir')
    parser.add_argument('--n-reps', '-n', type=int, default=1)
    parser.add_argument('--n-jobs', '-j', type=int, default=1)
    parser.add_argument('--tol', '-t', type=float, default=0.00001)
    args = parser.parse_args()

    if args.fcf_features:
        fcf = args.fcf_features.split(',')
    else:
        fcf = None

    if args.ff_features:
        ff = args.ff_features.split(',')
    else:
        ff = None

    main(args.data_file, args.patterns_file, fcf, ff,
         args.res_dir, args.n_reps, args.n_jobs, args.tol)
