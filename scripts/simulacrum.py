# First a directory called "input" in your working directory
import stimela, sys, numpy as np

INPUT = "/home/asad/data/minihalo/input"
OUTPUT = "/home/asad/data/minihalo/output"
MSDIR = "/home/asad/data/minihalo/msdir"

DIRECTIONS = { 
'0_MACS_J1115.8+0129'  :  'J2000,11h15m52.048s,+01d29m56.56s',
'1_RX_J0528.9-3927'  :  'J2000,05h28m53.039s,-39d28m15.53s',
'2_Abell_1063S'  :  'J2000,22h48m44.294s,-44d31m48.37s',
'3_Abell_85'  :  'J2000,00h41m50.406s,-09d18m10.79s',
'4_Abell_2204'  :  'J2000,16h32m46.92s,+05d34m32.86s',
'5_MACS_J1931.8-2634'  :  'J2000,19h31m49.656s,-26d34m33.99s',
'6_Abell_368'  :  'J2000,02h37m27.64s,-26d30m28.99s',
'7_Abell_1650'  :  'J2000,12h58m41.499s,-01d45m44.32s',
'8_RX_J0439.0+0715'  :  'J2000,04h39m00.71s,+07d16m07.65s',
'9_MACS_J1206.2-0847'  :  'J2000,12h06m12.276s,-08d48m02.4s'
}

START_TIMES = [
'UTC,2019/01/23/01:42:51.428571',
'UTC,2019/01/01/21:16:38.319328',
'UTC,2019/01/01/14:37:18.655462',
'UTC,2019/01/20/15:13:36.806723',
'UTC,2019/01/11/07:45:52.941176',
'UTC,2019/02/18/08:10:05.042017',
'UTC,2019/03/02/14:37:18.655462',
'UTC,2019/02/13/02:07:03.529412',
'UTC,2019/01/01/20:28:14.117647',
'UTC,2019/02/03/01:54:57.478992'
]

ROBUST = np.arange(-2,2.1,0.5)
PREFIX = "Cluster"

def simulate_observation(INPUT, OUTPUT, MSDIR, DIRECTION, START_TIME, ROBUST, PREFIX):
    stimela.register_globals()
    recipe = stimela.Recipe("MeerKAT sims - field {}".format(direction), ms_dir=MSDIR)

    ms = "{0}_{1}".format(PREFIX, direction)
    steps = []
    step = "makems_{}".format(i)
    recipe.add("cab/simms", step, {
        "msname"        : ms,
        "telescope"     : "meerkat",
        "date"          : START_TIMES[i],
        "synthesis"     : 1.3,
        #"scan-length"   : 0.25,
        "dtime"         : 60,
        "direction"     : DIRECTIONS[direction],
        "dfreq"         : "50MHz",
        "freq0"         : "900MHz",
        "nchan"         : 16,
    },  
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Create MS".format(step))
    steps.append(step)

    step = "plot_uv_{}".format(i)
    recipe.add("cab/casa_plotms", step, {
        "vis"       : ms, 
        "xaxis"     : "u",
        "yaxis"     : "v",
        "plotfile"  : "{0}_{1}_uv.png".format(PREFIX, direction)
    },  
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Plot uv-coverage".format(step))
    steps.append(step)
    
    step = "simnoise_{}".format(i)
    recipe.add("cab/simulator", step, {
        "msname"    : ms, 
        "addnoise"  : True,
        "sefd"      : 540,
        "column"    : "DATA",
        "smearing"  : False,
    },
        input=INPUT,
        output=OUTPUT,
        label="{0:s}:: Simulate noise".format(step))
    steps.append(step)

    for j,robust in enumerate(ROBUST):

        step = "image_{0}_{1}".format(i,j)
        recipe.add("cab/wsclean", step, {
            "msname"        : ms,
            "name"          : "{0}_{1}_{2}".format(PREFIX,direction,robust),
            "scale"         : 1,
            "size"          : 512,
            "niter"         : 0,
            "make-psf"      : True,
            "datacolumn"    : "DATA",
            "no-dirty"      : True,
            "weight"        : "briggs {}".format(robust),
        },
            input=INPUT,
            output=OUTPUT,
            label="{0:s}:: Image data".format(step))
        steps.append(step)

    recipe.run(steps)
    break
