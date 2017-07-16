#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import os

T = 24

cnt = dict({})

def readfile(out_filename,filename):
    zerocnt = 0
    onecnt = 0
    start_time = time.mktime(time.strptime('2010-08-01 00:00:00','%Y-%m-%d %H:%M:%S'))
    end_time = time.mktime(time.strptime('2011-03-01 00:00:00','%Y-%m-%d %H:%M:%S'))
    with open(filename,'r') as f:
        with open(out_filename,'w') as fout:
            for u_str,time_str,lat_str,lon_str,tmp1,tmp2,tmp3,tmp4 in csv.reader(f):
                u = int(u_str)
                cur_time = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
                dt = int((cur_time-start_time)/3600)
                t = dt % T
                dis_lat = int( ( float( lat_str ) - 35.0 ) / 0.008 )
                dis_lon = int( ( float( lon_str ) - 139.0 ) / 0.010 )
                if cur_time < end_time:
                    if (u,t,dis_lat,dis_lon) in cnt:
                        cnt[(u,t,dis_lat,dis_lon)] += 1
                    else:
                        cnt[(u,t,dis_lat,dis_lon)] = 1
                else:
                    if (u,t,dis_lat,dis_lon) in cnt:
                        zerocnt += 1
                        fout.write('{},{},{},{},0\n'.format(u_str,time_str,lat_str,lon_str))
                    else:
                        onecnt += 1
                        fout.write('{},{},{},{},1\n'.format(u_str,time_str,lat_str,lon_str))
            print 'Output {} success'.format(out_filename)
    return zerocnt,onecnt


def main():
    zerocnt = 0
    onecnt = 0
    # readfile('/home/fan/work/sadZDCDataSeparate/tokyo_area.csv')
    # zerocnt,onecnt = readfile('output.csv','/home/fan/work/data/1352090540/1352090540/00000007.csv')
    dirpath = '/home/fan/work/data/1352090540/1352090540'
    for filename in os.listdir(dirpath):
        full_path = os.path.join(dirpath,filename)
        if os.path.isfile(full_path):
            dzerocnt,donecnt = readfile('output/{}'.format(filename),full_path)
            zerocnt += dzerocnt
            onecnt += donecnt
    print 'zero count'
    print zerocnt
    print 'one count'
    print onecnt

if __name__ == '__main__':
    main()
