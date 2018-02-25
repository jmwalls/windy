#!/usr/bin/python3 -B
"""
NOAA National Centers for Environmental Information provides the following data
search:

https://www.ncdc.noaa.gov/cdo-web/search

We queried for Ann Abor (station KARB) daily summaries from 1998/11/01 until
present, 2018/02/22.

Data types represented in the daily log include:

    WSF2 - Fastest 2-minute wind speed
    FMTM - Time of fastest mile or fastest 1-minute wind
    WSF5 - Fastest 5-second wind speed
    WT03 - Thunder
    PRCP - Precipitation
    WT08 - Smoke or haze
    SNWD - Snow depth
    WDF2 - Direction of fastest 2-minute wind
    AWND - Average wind speed
    WDF5 - Direction of fastest 5-second wind
    WT10 - Tornado, waterspout, or funnel cloud"
    PGTM - Peak gust time
    WT01 - Fog, ice fog, or freezing fog (may include heavy fog)
    TMAX - Maximum temperature
    WT02 - Heavy fog or heaving freezing fog (not always distinguished from fog)
    TAVG - Average Temperature.
    TMIN - Minimum temperature
    TSUN - Total sunshine for the period
"""
import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _clean_wind_data(df):
    """Grab speed/direction and corresponding dates of fastest 5sec wind and
    remove nan values.
    """
    index = np.where(~np.isnan(df['WDF5']) & ~np.isnan(df['WSF5']))[0]
    return df['DATE'][index], df['WDF5'][index], df['WSF5'][index]


def _polar_histogram(ax, heading_rad, bins):
    """Plot histogram on ax for given heading data (in radians).
    """
    # convert heading to angle that will look correct on a polar plot.
    th = (-heading_rad + np.pi/2) % (2 * np.pi)

    width = 2 * np.pi / bins
    counts = np.array([len(np.where((th > width*i) &
                                    (th < width*(i + 1)))[0])
                       for i in range(bins)])
    theta = np.linspace(0., 2 * np.pi, bins, endpoint=False)
    radii = counts / counts.sum()
    ax.bar(theta, radii, width=width, bottom=0.01, color='k', alpha=0.5)
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--csv', help='input NCDS csv data file', required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    (date, wd, ws) = _clean_wind_data(df)

    hist_bins = 20

    fig = plt.figure()

    # plot all data
    ax = plt.subplot2grid((2, 8), (0, 0), rowspan=2, colspan=2, polar=True)
    _polar_histogram(ax, np.deg2rad(wd), hist_bins)
    ax.set_title('Wind dir KARB')

    # plot monthly data
    ax_mon = []
    for i in range(12):
        # find monthly data
        index = np.where([('-%02d-' % (i + 1)) in d for d in date])[0]
        wdi = wd[index]

        # plot
        r = int(i / 6)
        c = (i % 6) + 2  # 2 offset for first plot
        axi = plt.subplot2grid((2, 8), (r, c), polar=True)
        _polar_histogram(axi, np.deg2rad(wdi), hist_bins)
        axi.set_title('Mon %02d' % (i + 1))
        ax_mon.append(axi)

    plt.show()


if __name__ == '__main__':
    sys.exit(main())
