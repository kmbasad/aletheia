# Aletheia

Dependencies: `astropy`, `astroquery`, `scipy`

Install: `git clone https://github.com/kmbasad/aletheia`  

Go to the `scripts` directory.

To see the brightest sources (>100 mJy) from NVSS and SUMSS catalogs around a coordinate run:  
`python narcissus.py -c '325.063 -23.661' -r 1.5 -S`  
Where `-r` specifies the radius of the region to llok for.  
The red dotted lines show the FWHM and NULL at the highest frequency of MeerKAT L-band beam. And the blue lines show the same for the lowest frequency.  
The title of the plot will show the nearest MeerKAT calibrator name and distance.

To see the source track on any day run:  
`python auspicious.py -c '325.063 -23.661' -d '2019-1-1' -el 20 -S`  
where the date format is `year-month-day`

And to see how many hours a target stays close to its highest elevation (transit) throughout a year, just replace '2019-1-1' with '2019':  
`python auspicious.py -c '325.063 -23.661' -d '2019' -S`  

To see help files for either scripts use `-h` or `--help`

SOME EXAMPLE IMAGES ARE GIVEN IN THE WIKI.
