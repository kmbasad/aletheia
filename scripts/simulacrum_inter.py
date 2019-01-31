#!/usr/bin/env python
import stimela, sys, numpy as np

def simulate_observation(INPUT, OUTPUT, MSDIR, direction, start_time, robust, telescope='meerkat', name='Target',
    synthesis=5.,freq0="1350MHz", dfreq="10MHz", nband=1, nchan=10, sefd=420, dtime=60, img_px=257):
    #stimela.register_globals()
    recipe = stimela.Recipe("simulacrum {}".format(name), ms_dir=MSDIR)

    ms = name
    steps = []
    step = "makems"
    recipe.add("cab/simms", step, {
        "msname"        : ms,
        "telescope"     : telescope,
        "date"          : start_time,
        "synthesis"     : synthesis,
        #"scan-length"   : 0.25,
        "dtime"         : dtime,
        "direction"     : direction,
        "freq0"         : freq0,
        "dfreq"         : dfreq,
        "nband"         : nband,
        "nchan"         : nchan,
    },  
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Create MS".format(step))
    steps.append(step)

    step = "plot_uv"
    recipe.add("cab/casa_plotms", step, {
        "vis"       : ms, 
        "xaxis"     : "u",
        "yaxis"     : "v",
        "plotfile"  : "{0}_uv.png".format(name)
    },  
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Plot uv-coverage".format(step))
    #steps.append(step)

    step = "rfi_mask"
    recipe.add('cab/rfimasker', step, {
        "msname"  : ms,
        "mask"    : 'labelled_rfimask.pickle.npy',
        "accumulation_mode": 'or',
        "uvrange":'0~500'
    },
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Mask RFI".format(step))
    steps.append(step)
    
    step = "simnoise"
    recipe.add("cab/simulator", step, {
        "msname"    : ms, 
        "addnoise"  : True,
        "sefd"      : sefd,
        "column"    : "DATA",
        "smearing"  : False,
    },
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Simulate noise".format(step))
    steps.append(step)

    for j,r in enumerate(robust):

        step = "image_{0}".format(j)
        recipe.add("cab/wsclean", step, {
            "msname"        : ms,
            "name"          : "{0}_{1}".format(name,r),
            "scale"         : 1,
            "size"          : img_px,
            "niter"         : 0,
            "make-psf"      : True,
            "datacolumn"    : "DATA",
            "no-dirty"      : True,
            "weight"        : "briggs {}".format(r),
        },
            input=INPUT,
            output=OUTPUT,
            label="{0:s}:: Image data".format(step))
        steps.append(step)

    recipe.run(steps)

def minihalos(INPUT, OUTPUT, MSDIR, robust, synth=0.75):
    #Targets = {'MSJ2137': [u'J2000,21:40:15.178,-23:39:40.71', 'UTC,2019/06/20/00:42:21.176', 'UTC,2019/06/20/02:19:09.580'], 'A3444': [u'J2000,10:23:54.8,-27:17:09', 'UTC,2019/03/01/20:52:26.218', 'UTC,2019/03/01/22:29:14.622'], 'A1413': [u'J2000,11:55:19.4,+23:24:26', 'UTC,2019/03/01/21:52:56.471', 'UTC,2019/03/01/23:53:56.975'], 'MACSJ1115': [u'J2000,11:15:54.9,+01:29:56', 'UTC,2019/03/01/21:16:38.319', 'UTC,2019/03/01/23:17:38.824'], 'A1795': [u'J2000,13:48:55,+26:36:01', 'UTC,2019/04/01/21:52:56.471', 'UTC,2019/04/01/23:41:50.924']}
    Targets = {'MSJ2137': [u'J2000,21:40:15.178,-23:39:40.71', 'UTC,2019/06/20/01:38:33.199', 90], 'A3444': [u'J2000,10:23:54.8,-27:17:09', 'UTC,2019/03/01/20:29:27.989', 224], 'A1413': [u'J2000,11:55:19.4,+23:24:26', 'UTC,2019/03/01/23:05:11.279', 90], 'MACSJ1115': [u'J2000,11:15:54.9,+01:29:56', 'UTC,2019/03/01/22:28:16.716', 90], 'A1795': [u'J2000,13:48:55,+26:36:01', 'UTC,2019/04/01/21:51:53.021', 224]}

    for i,ii in enumerate(Targets):
        Target = Targets[ii]
        direction = Target[0]
        stime = Target[1]
        synth = Target[2]/60.

        tim = (stime.split('/')[1:])
        tag = tim[0]+'-'+tim[1]+'-'+tim[2].split(':')[0]
        prefix = "%s_%s_%.0fmin"%(ii,tag,synth*60.)
        print prefix

        simulate_observation(INPUT, OUTPUT, MSDIR, str(direction), str(stime), robust, telescope='meerkat', name=prefix, \
            synthesis=synth,freq0="900MHz", dfreq="20MHz", nband=1, nchan=39, sefd=420, dtime=60, img_px=256)

if __name__=='__main__':
    INPUT = "/home/asad/software/aletheia/data"
    PATH = "/home/asad/data/minihalo"
    OUTPUT = PATH+'/IMG'
    MSDIR = PATH+'/MS'

    robust = np.arange(-2,2.1,0.5)

    minihalos(INPUT, OUTPUT, MSDIR, robust)
