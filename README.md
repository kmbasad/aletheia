# Aletheia

Dependencies: `astropy`, `astroquery`, `scipy`

Clone: `git clone https://github.com/kmbasad/aletheia`  

Either run the individual scipts from within the `scripts` directory, or add that directory to your path using:

`PATH=/path/to/aletheia/scripts:$PATH`

## Find nearest sources

To see the brightest sources (>100 mJy) from NVSS and SUMSS catalogs around a coordinate run:  
`python narcissus.py -c '325.063 -23.661' -r 1.5 -S`  
Where `-r` specifies the radius of the region to look for.  

The red dotted lines show the FWHM and NULL at the highest frequency of MeerKAT L-band beam. And the blue lines show the same for the lowest frequency.  

The title of the plot will show the nearest MeerKAT calibrator name and distance.

## Find auspicious day for observation

To see the source track on any day run:  
`python auspicious.py -c '325.063 -23.661' -d '2019-1-1' -el 20 -V`  
where the date format is `year-month-day`

If you want to show the distance to the nearest satellite on the same plot add the `-S` option:
`python auspicious.py -c '325.063 -23.661' -d '2019-1-1' -V -S`  
CAUTION: this takes a long time; the task is parallelized, so please use a suitable cluster.

To see how many hours a target stays close to its highest elevation (transit) throughout a year, just replace '2019-1-1' with '2019':  
`python auspicious.py -c '325.063 -23.661' -d '2019' -S`  

To see help files for either scripts use `-h` or `--help`

SOME EXAMPLE IMAGES ARE GIVEN IN THE WIKI.
