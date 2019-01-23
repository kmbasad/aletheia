# Aletheia

Install: `git clone https://github.com/kmbasad/aletheia`  

Go to the `scripts` directory.

To see the brightest sources (>100 mJy) from NVSS and SUMSS catalogs around a coordinate run:  
`python narcissus.py -c '325.063 -23.661' -S`  
The title of the plot will show the nearest MeerKAT calibrator name and distance.

To see the source track on any day run:  
`python auspicious.py -c '325.063 -23.661' -d '2019-1-1' -el 20 -S`  

And to see how many hours a target stays close to its highest elevation (transit) throughout a year, just replace '2019-1-1' with '2019':  
`python auspicious.py -c '325.063 -23.661' -d '2019' -S`  

To see help files for either scripts use `-h` or `--help`
