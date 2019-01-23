#!/usr/bin/env python
from astroquery.vizier import Vizier
import matplotlib.colors as mc
import astropy.coordinates as co
from astropy import units as u
import argparse
import scipy.constants as sc
import matplotlib.pyplot as plt, numpy as np

def meerkat_calibrator(tc):
    l = open('../data/meerkat_calibrators.csv', 'r').readlines()[1:]
    cal = np.array([i.strip().split(',') for i in l])

    for i in range(cal.shape[0]):
        r = co.Angle("%s hours"%cal[i,2])
        cal[i,2] = r.deg
        d = co.Angle("%s deg"%cal[i,3])
        cal[i,3] = d.deg

    cc = co.SkyCoord(ra=cal[:,2], dec=cal[:,3], unit='deg')

    idx, d2d, d3d = tc.match_to_catalog_sky(cc)

    return cal[idx], d2d

def good_channels(nu):
    bads=([856,870], [920,960], [1125,1305], [1380,1384], [1463,1492], [1520,1630], [1670,1720])
    ind = []
    for bad in bads:
        ind.append(np.where((nu>=bad[0]) & (nu<=bad[1])))   
    flatten = lambda l: [item for sublist in l for item in sublist[0]]
    all = range(len(nu))
    bads = flatten(ind)
    goods = list(set(all)-set(bads))
    return goods, bads

def meerkat_beamwidth(plot=False):
    nu = np.arange(856,856+857)
    g, b = good_channels(nu)

    l = open('../data/meerkat_m017_beamwidth.txt', 'r').readlines()
    d = [i.strip().split(',') for i in l[1:]]
    bw = []
    for i in range(len(d)):
        dd = map(float, d[i])
        bwx = (dd[0]+dd[1])/2.
        bwy = (dd[2]+dd[3])/2.
        bw.append((bwx+bwy)/2.*(180./np.pi))
    bw = np.array(bw)
    plt.figure(figsize=(7,5))
    y = np.zeros(len(nu))
    y[g] = bw
    bw_intp = np.interp(nu, nu[y!=0.], y[y!=0.])[44:815]
    f = nu[44:815]

    params = np.polyfit(f, bw_intp, deg=4)
    p = np.poly1d(params)

    nug = nu[g][29:]
    bwg = bw[29:]
    if plot:
        plt.plot(nug, bwg, '.', markersize=1, color='r', label='Holographic')
        plt.plot(f, p(f), ':', color='blue', label='Polynomial fit')
        plt.plot(f, 1.2*((sc.c/(f*1e6))/14.)*(180./np.pi), 'g--', label='Theoretical')
        a = plt.xlim([900,1672])

        a = plt.ylim([0.88,1.65])
        a = plt.legend()
        plt.xlabel('Frequency [MHz]')
        plt.ylabel('Beamwidth [degree]')
        plt.grid()

    fwhm = np.array([bwg.min()/2., bwg.max()/2.])
    null = fwhm*1.699
    return fwhm, null

def nearest_sources(cc, cat='NVSS', bacat='SUMSS', radius=1.5, show=True, filename='nearest_bright_sources.png'):
    Vizier.ROW_LIMIT = -1
    cr, cd = cc.ra.value, cc.dec.value
    try:
        p = Vizier.query_region("%f %f"%(cr,cd), radius=radius*u.degree, catalog=cat)
        S = p[0][:]['S1.4']
    except:
        p = Vizier.query_region("%f %f"%(cr,cd), radius=radius*u.degree, catalog=bacat)
        S = p[0][:]['St']
    positions = co.SkyCoord(ra=co.Angle(p[0][:]['RAJ2000'], unit=u.hour), dec=co.Angle(p[0][:]['DEJ2000'], unit=u.deg))
    field = p[0]
    flux = S

    vmin, vmax = 100, 1e3

    fig = plt.figure(figsize=(7.5,6))
    ax = fig.add_subplot(111)
    ind = np.where(flux>=vmin)
    pos = positions[ind]
    fl = flux[ind]
    
    ax.scatter(cr, cd, 100, marker='o', color='black', alpha=0.5)
    dist = cc.separation(pos)
    vmax=fl.max()
    cb_data = ax.scatter(x=pos.ra.deg, y=pos.dec.deg, s=200, c=fl, alpha=0.7, \
                      norm=mc.Normalize(vmin=vmin,vmax=vmax), cmap='rainbow')
    a = ax.set_xlim([cr-radius,cr+radius])
    b = ax.set_ylim([cd-radius,cd+radius])

    fwhm, null = meerkat_beamwidth()

    ax.add_artist(plt.Circle((cr,cd), fwhm[0], fill=False, color='red', linestyle='--'))
    ax.add_artist(plt.Circle((cr,cd), null[0], fill=False, color='red', linestyle='--'))
    ax.add_artist(plt.Circle((cr,cd), fwhm[1], fill=False, color='blue', linestyle='--'))
    ax.add_artist(plt.Circle((cr,cd), null[1], fill=False, color='blue', linestyle='--'))
    r = radius
    ax.set_xticks([cr-r,cr-r/2.,cr,cr+r/2.,cr+r])
    ax.set_yticks([cd-r,cd-r/2.,cd,cd+r/2.,cd+r])

    plt.axes().set_aspect('equal', 'datalim')
    ax.grid()
    ax.set_xlabel('Right ascension')
    ax.set_ylabel('Declination')
    cb = fig.colorbar(cb_data)
    cb.set_label('Flux density [mJy]')


    cal, d2d = meerkat_calibrator(cc)
    cal = cal[0].split(' | ')[0]
    ax.set_title("Calibrator: %s ($%.2f^\\circ$)"%(cal,d2d.deg), fontsize=12)

    if show: plt.show()
    else: fig.tight_layout(); fig.savefig(filename, dpi=80)
    
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Show the nearest brightest sources around a coordinate')
    parser.add_argument('-c', '--coord', help="Coordinate as '325:03:47.67 -23:39:40.71' or '325.063 -23.661'", type=str, required=True)
    parser.add_argument('-r', '--radius', help="Radius of the region", type=float, default=1.5, required=False)
    parser.add_argument('-S', '--show', help="Add '-S' to show the plot. By default it will be saved as png", action='store_true', \
        default=False, required=False)
    args = parser.parse_args()

    c = args.coord.split(' ')
    if len(c[0].split())==3: cc = co.SkyCoord(ra=c[0], dec=c[1], unit=(u.hourangle, u.deg))
    elif len(c[0].split())==1: cc = co.SkyCoord(ra=c[0], dec=c[1], unit='deg')
    else: raise Exception('The sky coordinate format is wrong')
    nearest_sources(cc, radius=args.radius, show=args.show)
