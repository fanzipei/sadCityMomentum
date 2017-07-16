#!/usr/bin/env python
# encoding: utf-8

import csv
import os

def separateregion(outfn,dirpath):
    with open(outfn,'w') as outfp:
        for filename in os.listdir(dirpath):
            full_path = os.path.join(dirpath,filename)
            if os.path.isfile(full_path):
                print 'Reading {}'.format(filename)
                for u_str,time_str,lat_str,lon_str,tmp1,tmp2 in csv.reader(open(full_path,'r')):
                    lat = float(lat_str)
                    lon = float(lon_str)
                    if lat > 35.5 and lat < 35.8 and lon > 139.4 and lon < 139.9:
                        outfp.write('{},{},{},{}\n'.format(u_str,time_str,lat_str,lon_str))
                print 'Complete'

def main():
    separateregion('/home/fan/latex/UbiComp2015_presentation/data/regulardays.csv','/media/fan/65D42DD030E60A2D/ZDC/2012/ForPresentation/')

if __name__ == '__main__':
    main()
