from skyfield.api import Topos, load

def angular_separation(ra, dec, phase_centre):
    """
    Calculates the angular separation between a source and the phase centre.
    Parameters
    ----------
    ra : float
        Right-ascension of the source in radians.
    dec : float
        Declination of the source in radians.
    phase_centre : tuple
        Right-ascension and declination of the phase centre in radians.
    Returns
    ------
    theta : float
        The angular separation between the phase centre and given source in
        degrees.
    """
    ra1, dec1 = [ra, dec]
    ra2, dec2 = phase_centre

    theta = np.arccos(np.sin(dec1)*np.sin(dec2) + \
            np.cos(dec1)*np.cos(dec2)*np.cos(ra1-ra2))

    return theta

def get_sat_tles(geostationary=True):
    '''
    Collect the satellite TLEs that fall in the L-Band.
    
    Parameters
    ----------
    geostationary: boolean
        Include geostationary staellites or not.
    
    Returns
    -------
    sats: dictionary
        Satellite TLEs ready for consumption by Skyfield.
    '''
    
    source_url = 'https://www.celestrak.com/NORAD/elements/'
    gps_tles = ['gps-ops.txt', 'glo-ops.txt', 'beidou.txt', 'galileo.txt', 'sbas.txt', ]
    comms_tles = ['iridium.txt', 'iridium-NEXT.txt', 'geo.txt']
    if geostationary:
        LbandSats = gps_tles + comms_tles
    else:
        LbandSats = gps_tles + comms_tles[:-1]
    
    sats = {}
    for i in range(len(LbandSats)):
        sats.update(load.tle(source_url+LbandSats[i]))
        
    return sats


def sat_separations(params):
    '''
    Separation between a source and set of satellites.
    
    Parameters
    ----------
    params: list
        [[source_ra, source_dec], date]
    source_ra: float
        Right Ascension of source in radians.
    source_dec: float
        Declination of source in radians.
    date: time object
        Date and time of observation.
        
    Returns
    -------
    separations: array
        Angular separation between each satellite and the source in degrees.
    '''
    
    source, t = params
    
    source_ra, source_dec = source
    
    satellites = get_sat_tles()
    
    tt = ts.utc(*[int(x) for x in t.strftime('%Y %m %d %H %M %S').split()])
    mkat = Topos('30.7130 S', '21.4430 E')
    
    separations = np.zeros((len(satellites.items())))
    
    for j, sat in enumerate(satellites.items()):

        sat_ra, sat_dec = [(sat[1]-mkat).at(tt).radec(ts.J2000)[i].radians for i in range(2)]
        separations[j] = np.rad2deg(angular_separation(sat_ra, sat_dec, [source_ra, source_dec]))
    
    return separations 


