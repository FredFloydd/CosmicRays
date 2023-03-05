import os
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import scipy.stats as stat
from data_methods import rotate_map, rotate_map_sim
from argparse import ArgumentParser

# Parser for reading command line arguments
parser = ArgumentParser()
parser.add_argument("-f", "--file", type=str, default='nside=64.npz')
parser.add_argument("-p", "--path", type=str, default='../figs/')
parser.add_argument("-o", "--outdir", type=str, default='../figs/')

counter = 38

args = parser.parse_args()
args_dict = vars(args)

# Read in data file
filename = args.path + args.file
data = np.load(filename)

# Read in data
flux_maps = data['flux']
flux_maps_final = data['flux_final']
time_maps = data['time']
kolmogorov_dist_maps = data['kolmogorov']
bin_limits = data['bin_limits']
limits = data['limits']
bins = data['bins']
widths = data['widths']

# Physical constants for scaling energy
c = 299792458
e = 1.60217663 * 10 ** (-19)
m_p = 1.67262192 * 10 ** (-27)
energy_factor = 1 / (m_p * c * c / (e * 10 ** 12))

# Plot binned tests
bin_counter = 0
for i in range(len(bins)):
    binning = bin_limits[i]
    for j in range(bins[i]):
        lower_limit = binning[j] / energy_factor
        upper_limit = binning[j + 1] / energy_factor

        plt.set_cmap('coolwarm')
        hp.visufunc.mollview(np.log10(flux_maps[bin_counter] / stat.gmean(flux_maps[bin_counter])),
                             title=f'Relative intensity at Earth for ' + "{0:.3g}".format(lower_limit) +
                                   ' TeV < E < ' + "{0:.3g}".format(upper_limit) + ' TeV',
                             unit="log(Flux)",
                             max=np.log10(2),
                             min=np.log10(0.5))
        hp.graticule()
        plt.savefig(args.outdir + f'flux/flux_map_num_bins={bins[i]}_bin={j}')

        plt.clf()

        power = hp.anafast(flux_maps[bin_counter])
        plt.plot(np.log10(power))
        plt.savefig(args.outdir + f'power/power_spectrum_num_bins={bins[i]}_bin={j}')

        plt.clf()

        plt.set_cmap('coolwarm')
        hp.visufunc.mollview(flux_maps_final[bin_counter],
                             title=f'Relative intensity at edge of simulation for ' + "{0:.3g}".format(lower_limit) +
                                   ' TeV < E < ' + "{0:.3g}".format(upper_limit) + ' TeV',
                             unit="Flux",
                             min=0.999)
        hp.graticule()
        plt.savefig(args.outdir + f'flux_final/flux_map_final_num_bins={bins[i]}_bin={j}')

        '''
        plt.set_cmap('coolwarm')
        hp.visufunc.mollview(np.log10(time_maps[bin_counter]),
                             title=f'Time skymap for ' + "{0:.3g}".format(lower_limit) +
                                   ' TeV < E < ' + "{0:.3g}".format(upper_limit) + ' TeV',
                             unit="Log(Time /s)",
                             min=np.min(np.log10(time_maps)),
                             max=np.max(np.log10(time_maps)))
        hp.graticule()
        plt.savefig(args.outdir + f'time/time_map_num_bins={bins[i]}_bin={j}')
        plt.clf()
        '''
        bin_counter += 1

limits_counter = 0
for i in range(len(limits)):
    lower_limit = limits[i][0]
    upper_limit = limits[i][1]
    for j in range(len(widths)):
        width = widths[j]
        p_values = kolmogorov_dist_maps[limits_counter]

        plt.set_cmap('bone')
        hp.visufunc.mollview(np.abs(p_values),
                             title=f'Kolmogorov-Smirnov P-Values for ' + "{0:.3g}".format(lower_limit) +
                                   ' TeV < E < ' + "{0:.3g}".format(upper_limit) + ' TeV',
                             unit="P")
        hp.graticule()
        plt.savefig(args.outdir + f'kolmogorov-p/kolmogorov_map_p_limit={i+counter}_width={width}')

        signs = np.sign(p_values)
        z_values = np.maximum(stat.norm.ppf(1 - np.abs(p_values)), 0) * signs

        plt.set_cmap('coolwarm')

        hp.visufunc.mollview(z_values,
                             title=f'Kolmogorov-Smirnov Z-Scores for ' + "{0:.3g}".format(lower_limit) +
                                   ' TeV < E < ' + "{0:.3g}".format(upper_limit) + ' TeV',
                             unit="Sigma",
                             min=-5,
                             max=5)
        hp.graticule()

        plt.savefig(args.outdir + f'kolmogorov-z/kolmogorov_map_z_limit={i+counter}_width={width}')

    limits_counter += 1
