#!/usr/local/bin/python

import numpy as np
import healpy as hp
from data_methods import create_bin_sizes, bin_particles, create_reweighed_sky_maps, create_time_maps
from statistical_methods import perform_kolmogorov_smirnov
from argparse import ArgumentParser

# Parser for reading command line arguments
parser = ArgumentParser()
parser.add_argument("-l", "--limits", type=str, default='./limits',
                    help="File containing limits for distribution tests")
parser.add_argument("-b", "--bins", type=str, default='./bins',
                    help="File containing binning schemes for binned tests")
parser.add_argument("-w", "--widths", type=str, default='./widths',
                    help="File containing strip widths for strip tests")
parser.add_argument("-p", "--path", type=str, default='../data/',
                    help="Path to data file")
parser.add_argument("-f", "--file", type=str, default='nside=16num_bins=10.npz')
parser.add_argument("-o", "--output", type=str, default='../figs/',
                    help="Output directory for figure data")

args = parser.parse_args()
args_dict = vars(args)

# Read in files
limits = np.loadtxt(args.limits)
bins = np.loadtxt(args.bins, dtype=int)
widths = np.loadtxt(args.widths, dtype=int)

data_path = args.path + args.file
data = np.load(data_path, allow_pickle=True)

# We need particle data
particles = 0

# Read in data from file
for key in data:
    if key == 'particles':
        particles = data[key]

npix = len(particles)
nside = hp.npix2nside(npix)
num_binnings = len(bins)
num_limits = len(limits)
num_widths = len(widths)
max_bins = np.max(bins)

# Create initial arrays to be written to by each of the tests
reweighed_maps = []
time_maps = []
chi_squared_flux_maps = []
chi_squared_distribution_maps = []
kolmogorov_smirnov_distribution_maps = []
bin_limits = []

'''

EVERYTHING IS IN SIMULATION UNITS CURRENTLY, NOT TEV

'''

# Do binned tests for each binning
for binning in bins:
    # Sort particle data into energy bins
    bin_sizes = create_bin_sizes(particles, binning)
    bin_limits.append(np.pad(bin_sizes, (0, 1 + max_bins - len(bin_sizes))))
    binned_particles = bin_particles(particles, bin_sizes)

    # Create reweighed flux maps
    print(f'Creating reweighed flux maps for {binning} energy bins')
    reweighed_maps = [*reweighed_maps, *create_reweighed_sky_maps(binned_particles)]

    # Create time map
    print(f'Creating time averaged maps for {binning} energy bins')
    time_maps = [*time_maps, *create_time_maps(binned_particles)]

    # Perform statistical tests for each width
    for width in widths:
        # Create chi squared flux maps
        print(f'Performing chi squared test on flux maps for {binning} energy bins and width = {width}')

        # Create chi squared distribution maps
        print(f'Performing chi squared test on distribution maps for {binning} energy bins and width = {width}')

# Perform KS test for each set of limits and widths
for limit in limits:
    for width in widths:
        print(f'Performing Kolmogorov-Smirnov test on distribution with lower = {limit[0]} TeV, upper = {limit[1]} '
              f'TeV and width = {width}')
        ks_map = perform_kolmogorov_smirnov(particles, limit, width)
        kolmogorov_smirnov_distribution_maps.append(ks_map)

# Save all produced data

prefix = 'nside=' + str(nside)
output_name = args.output + prefix
print("saving %s" % output_name)
np.savez_compressed(output_name,
                    flux=reweighed_maps,
                    time=time_maps,
                    chisquareflux=chi_squared_flux_maps,
                    chisquaredist=chi_squared_distribution_maps,
                    kolmogorov=kolmogorov_smirnov_distribution_maps,
                    binlimits=bin_limits,
                    limits=limits,
                    bins=bins,
                    widths=widths)