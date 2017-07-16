#!/usr/bin/env python
# encoding: utf-8

import csv
import time

TIME_INTERVAL = 600

traj_set = dict({})

def itemgetter(item):
    return item[2]

def main():
    start_time = time.mktime(time.strptime('2011-12-31 00:00:00','%Y-%m-%d %H:%M:%S'))
    with open('/home/fan/work/data/CityMomentum/tokyoarea_newyear.csv','r') as f:
        for u_str,time_str,lat_str,lon_str in csv.reader(f):
            cur_time = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            dt = int((cur_time-start_time)/TIME_INTERVAL)
            if dt not in traj_set:
                traj_set[dt] = [(u_str,time_str,cur_time,lat_str,lon_str)]
            else:
                traj_set[dt].append((u_str,time_str,cur_time,lat_str,lon_str))

    for dt in traj_set:
        sorted( traj_set[dt] , key = itemgetter )

    for dt in traj_set:
        with open('/home/fan/work/data/CityMomentum/10min_newyear/D{}T{}.csv'.format(dt/144,dt%144),'w') as f:
            for u_str,time_str,cur_time,lat_str,lon_str in traj_set[dt]:
                f.write('{},{},{},{}\n'.format(u_str,time_str,lat_str,lon_str))

if __name__ == '__main__':
    main()
