#!/usr/bin/env python
# encoding: utf-8

import csv
import random
import time

cluster = dict({})
traj_noise = dict({})

start_time = 50

def main():
    with open('./C80_clustering/usercluster_55.csv','r') as f:
        for u_str,k_str in csv.reader(f):
            cluster[int(u_str)] = int(k_str)
            traj_noise[int(u_str)] = ( random.uniform(-0.002,0.002) , random.uniform(-0.0025,0.0025) )

    fout = [open('output{}.csv'.format(i),'w') for i in xrange(10)]
    fout_combine = open('output.csv','w')
    fout_pseudo = [open('output_pseudo_{}.csv'.format(i),'w') for i in xrange(10)]
    # fout_pseudo_combine = open('output_pseudo.csv','w')

    for i in xrange(6):
        with open('/home/fan/work/data/CityMomentum/10min_c80/D{}T{}.csv'.format((start_time+i)/144,(start_time+i)%144),'r') as f_data:
            for u_str,time_str,lat_str,lon_str in csv.reader(f_data):
                u = int(u_str)
                t = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
                t = int( t / 60 ) * 60
                if u in cluster:
                    k = cluster[u]
                    fout[k].write('{},{},{},{}\n'.format(u_str,time_str,lat_str,lon_str))
                    fout_combine.write('{},{},{},{},{}\n'.format(u_str,time_str,lat_str,lon_str,k))
                    range_lat,range_lon = traj_noise[u]
                    center_lat = int( ( float(lat_str) ) / 0.016 ) * 0.016 + 0.008
                    center_lon = int( ( float(lon_str) ) / 0.020 ) * 0.020 + 0.010
                    lat = center_lat + range_lat
                    lon = center_lon + range_lon
                    fout_pseudo[k].write('{},{},{},{}\n'.format(u_str,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t)),lat,lon))
                    fout_combine.write('{},{},{},{},{}\n'.format(u_str,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t)),lat,lon,k))

if __name__ == '__main__':
    main()
