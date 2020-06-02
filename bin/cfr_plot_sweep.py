#!/usr/bin/env python
#
# Generate data in a parameter sweep and create plots.

import os
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from cymr import models
from cymr import network
from cfr import framework
from psifr import fr


def main(data_file, patterns_file, param1, sweep1, param2, sweep2,
         res_dir, n_rep=1):

    # run individual parameter search
    data = pd.read_csv(data_file)
    model = models.CMRDistributed()
    wp = framework.model_variant(['loc', 'cat', 'use'], None)
    patterns = network.load_patterns(patterns_file)

    # fixed parameters
    fixed = {'Afc': 0, 'Acf': 0, 'Aff': 0, 'Dff': 1,
             'Lfc': .16, 'Lcf': .08, 'P1': .14, 'P2': 1.3,
             'B_enc': .75, 'B_start': .87, 'B_rec': .95, 'T': .10,
             'X1': .0078, 'X2': .26, 'Dfc': .84, 'Dcf': .92,
             'w0': .5, 'w1': .5}

    # run sweep
    study_data = data.loc[(data['trial_type'] == 'study')]
    param_names = [param1, param2]
    param_sweeps = [sweep1, sweep2]
    results = model.parameter_sweep(study_data, fixed, param_names, param_sweeps,
                                    dependent=wp.dependent, patterns=patterns,
                                    weights=wp.weights, n_rep=n_rep)

    # prep for analysis
    sim = results.groupby(level=[0, 1]).apply(
        fr.merge_free_recall, study_keys=['category', 'item_index']
    )
    sim1 = sim.loc[sim['list'] <= 48]

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    kws = {'height': 4}

    # serial position curve
    p = sim.groupby(level=[0, 1]).apply(fr.spc)
    g = fr.plot_spc(p.reset_index(), row=param_names[0], col=param_names[1],
                    **kws)
    g.savefig(os.path.join(res_dir, 'spc.pdf'))

    # lag crp for output position > 3
    p = sim.groupby(level=[0, 1]).apply(fr.lag_crp, item_query='output > 3')
    g = fr.plot_lag_crp(p.reset_index(), row=param_names[0],
                        col=param_names[1], **kws)
    g.savefig(os.path.join(res_dir, 'lag_crp.pdf'))

    # category crp
    p = sim.groupby(level=[0, 1]).apply(
        fr.category_crp, category_key='category'
    )
    g = sns.relplot(kind='scatter', x=param_names[0], y=param_names[1],
                    hue='prob', data=p.reset_index(), height=5)
    g.savefig(os.path.join(res_dir, 'cat_crp.pdf'))

    # semantic crp
    edges = np.linspace(0, .4, 5)
    rsm = patterns['similarity']['use']
    p = sim.groupby(level=[0, 1]).apply(
        fr.distance_crp, 'item_index', rsm, edges
    )
    g = fr.plot_distance_crp(p.reset_index(), row=param_names[0],
                             col=param_names[1], **kws)
    g.set(ylim=[0, .2])
    g.savefig(os.path.join(res_dir, 'use_crp.pdf'))

    # raster by serial position
    g = fr.plot_raster(fr.reset_list(sim1.reset_index()),
                       row=param_names[0], col=param_names[1],
                       orientation='horizontal', length=4)
    g.savefig(os.path.join(res_dir, 'raster_input.pdf'))

    # raster by category
    g = fr.plot_raster(fr.reset_list(sim1.reset_index()), hue='category',
                       palette=sns.color_palette('Set2', 3),
                       row=param_names[0], col=param_names[1],
                       orientation='horizontal', length=4)
    g.savefig(os.path.join(res_dir, 'raster_category.pdf'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file')
    parser.add_argument('patterns_file')
    parser.add_argument('param1')
    parser.add_argument('sweep1')
    parser.add_argument('param2')
    parser.add_argument('sweep2')
    parser.add_argument('res_dir')
    parser.add_argument('--n-rep', '-n', type=int, default=1)
    args = parser.parse_args()
    s1 = np.asarray(args.sweep1.split(','), dtype=float)
    s2 = np.asarray(args.sweep2.split(','), dtype=float)
    main(args.data_file, args.patterns_file, args.param1, s1, args.param2, s2,
         args.res_dir, args.n_rep)
