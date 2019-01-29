#!/usr/bin/env python
import numpy as np
import astropy.coordinates as co
from astropy import units as u
from astropy.time import Time
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import argparse
from parallelize import parmap
from geokentrikos import sat_separations

def best_times_day(coord, lat=-30.7133, lon=21.443, utcoff=2., date='2019-01-01', plot=True, show=False,\
                 distsun=5, distmoon=3, elev=20, night=False, leg=None, setrise=True, filename='auspiciousness_day.png'):
    location = co.EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=1e3*u.m)
    utcoffset = utcoff*u.hour
    timesteps = 120
    delta_time = np.linspace(-12, 12, timesteps)*u.hour
    ind = range(0,len(delta_time))

    midnight = Time(date) - utcoffset
    times = midnight + delta_time
    frame = co.AltAz(obstime=times, location=location)

    sun = co.get_sun(times).transform_to(frame)
    moon = co.get_moon(times).transform_to(frame)
    src = coord.transform_to(frame)
    ind_riseset = np.where(np.logical_and(sun.alt>-12*u.deg, sun.alt<12*u.deg))[0]
    ind_sun = np.where(src.separation(sun).deg<distsun)[0]
    ind_moon = np.where(src.separation(moon).deg<distmoon)[0]
    alt_max = src.alt.max()
    ind_low = np.where(src.alt<=(alt_max-alt_max*(elev/100.)))[0]

    if night==True: ind_day = np.where(sun.alt>0*u.deg)[0]
    else: ind_day = [None]

    g = np.sort(list(set(ind)-set(ind_riseset)-set(ind_sun)-set(ind_moon)-set(ind_low)-set(ind_day)))
    try: tg = delta_time[g]
    except: tg = None

    if satellites:
        sat_times = [times[g][0]+i*timedelta(minutes=1) for i in range(int((tg[-1]-tg[0]).to(u.minute)/u.minute))]
        params = [list(i) for i in zip([[coord.ra.rad, coord.dec.rad] for i in range(len(sat_times))], sat_times)]
        min_seps = np.nanmin(np.array(parmap(sat_separations, params)), axis=1)
        sat_time_steps = np.linspace(delta_time[g][0], delta_time[g][-1], len(min_seps))
        sat_frame = co.AltAz(obstime=sat_times, location=location)
        sat_alts = coord.transform_to(sat_frame).alt

    if plot==True:
        plt.plot(delta_time, sun.alt, 'r--', label='Sun')
        plt.plot(delta_time, moon.alt, 'b--', label='Moon')
        plt.fill_between(delta_time.to('hr').value, 0, 90, np.logical_and(sun.alt<12*u.deg,sun.alt>-12*u.deg), \
                 color='0.5', alpha=0.5)
        plt.fill_between(delta_time.to('hr').value, 0, 90, sun.alt<0*u.deg, color='0.9', alpha=0.7)
        plt.plot(delta_time, src.alt, 'g-', label='Target')
        if satellites:
            try: cb = plt.scatter(sat_time_steps, sat_alts, c=min_seps, s=30, alpha=0.5, vmin=0, vmax=10)
            except: None
        else:
            try: plt.scatter(delta_time[g], src.alt[g], s=30, c='g', alpha=0.5, label='Best time')
            except: None
        plt.ylim(0,90)
        plt.xlim(-12,12)
        plt.xticks(range(-12,13,2))
        plt.legend(loc='best', ncol=2)
        plt.grid()
        plt.title(date)
        plt.xlabel('Time from midnight [hour]')
        plt.ylabel('Elevation [degree]')
        if satellites:
            cbar = plt.colorbar(cb)
            cbar.set_ticks(np.arange(0, 11, 2))
            cbar.set_label('Angular separation from closest satellite\n[degree]',
                           rotation=270, labelpad=+20)
        if show: plt.show()
        else: plt.tight_layout(); plt.savefig(filename, dpi=80)

    else: return tg

def best_times_year(c, year=2019, lat=-30.7133, lon=21.443, utcoff=2., delta=15, elev=20., night=False, show=True, \
    filename='auspiciousness_year.png', distsun=5, distmoon=3):
    start = datetime.strptime(str(year)+'-1-1', "%Y-%m-%d")
    stop = datetime.strptime(str(year+1)+'-1-1', "%Y-%m-%d")
    goods = []
    while start < stop:
        print(start.year, start.month, start.day)
        g = best_times_day(c, lat=lat, lon=lon, utcoff=utcoff, date=start, plot=False, elev=elev, night=night, distsun=distsun,distmoon=distmoon)
        goods.append(g)
        start = start + timedelta(days=delta)

    TR, TT = [], []
    delta_time = np.linspace(0, 24, 120)*u.hour
    for i in range(len(goods)):
        g = goods[i]
        try:
            TR.append((g[-1]-g[0]).value)
            TT.append((len(g)-1.)/len(delta_time)*24.)
        except:
            TR.append(None)
            TT.append(None)
    TT = np.array(TT)
    days = np.linspace(1, 366, len(TT))
    fig = plt.figure(figsize=(10,4))
    plt.plot(days, TT, 'r.:', markersize=10, alpha=0.5)
    #ind = np.where(np.logical_and(TT>=3.0,np.array(TR)<4.3))
    #plt.plot(days[ind], np.array(TR)[ind], 'g.', markersize=3, alpha=0.5)

    plt.xticks([1,31,59,90,120,151,181,212,243,273,304,334,365],\
            ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct', 'Nov','Dec',''])
    plt.xlim(0,366)
    plt.ylim(0,4.)
    plt.ylabel('Good times [hour]')
    plt.title("%s (%i)"%(c.to_string('hmsdms'),year))
    plt.grid()

    if show: plt.show()
    else: plt.tight_layout(); plt.savefig(filename, dpi=80)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Calculate whether this day is auspicious for your observation or not')
    parser.add_argument('-c', '--coord', help="Coordinate as '325:03:47.67 -23:39:40.71' or '325.063 -23.661'", type=str, required=True)
    parser.add_argument('-d', '--date', help='Date as 2019-1-1 or year as 2019', default='2019-05-15', type=str, required=False)
    parser.add_argument('-l', '--latlon', help="Latitude and longitude of the telescope as '-30.7133 21.443'", default='-30.7133 21.443', type=str, required=False)
    parser.add_argument('-u', '--utc', help='UTC offset of the local time', default=2., type=float, required=False)
    parser.add_argument('-su', '--dist_sun', help='Minimum distance to the sun', default=5., type=float, required=False)
    parser.add_argument('-mo', '--dist_moon', help='Minimum distance to the moon', default=3., type=float, required=False)
    parser.add_argument('-el', '--elcut', help='Target elevation cut from the maximum in percent', default=20., type=float, required=False)
    parser.add_argument('-N', '--night', help="Add '-N' to observe only at night?", action='store_true', required=False)
    parser.add_argument('-S', '--show', help="Add '-S' to show the plot. By default it will be saved as png", action='store_true', default=False, required=False)
    parser.add_argument('-f', '--filename', help="Output filename: jpg,png,pdf", default='auspiciousness.png', required=False)
    args = parser.parse_args()

    dat = args.date.split('-')
    c = args.coord.split(' ')
    if len(c[0].split())==3: cc = co.SkyCoord(ra=c[0], dec=c[1], unit=(u.hourangle, u.deg))
    elif len(c[0].split())==1: cc = co.SkyCoord(ra=c[0], dec=c[1], unit='deg')
    else: raise Exception('The sky coordinate format is wrong')
    lat, lon = float(args.latlon.split(' ')[0]), float(args.latlon.split(' ')[1])

    if len(dat)==3:
        g = best_times_day(cc, lat=lat, lon=lon, utcoff=args.utc, date=args.date, night=args.night, elev=args.elcut, show=args.show,\
            distsun=args.dist_sun, distmoon=args.dist_moon, filename=args.filename)
    elif len(dat)==1:
        best_times_year(cc, year=int(args.date), lat=lat, lon=lon, utcoff=args.utc, night=args.night, elev=args.elcut, show=args.show,\
         distsun=args.dist_sun, distmoon=args.dist_moon, filename=args.filename)
    else: raise Exception('The date format is wrong')
