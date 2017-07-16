#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import math
import numpy as np

K = 10

# start_time = 132
# start_time = 90

def main():
    for t in xrange(6,3*144):
        citymomentum(t)

def citymomentum(cur_t):
    cluster = {}
    lastloc = {}
    graph = [{} for i in xrange(K)]
    with open('./C80_clustering/usercluster_{}.csv'.format(cur_t),'r') as f:
        for u_str,k_str in csv.reader(f):
            cluster[int(u_str)] = int(k_str)

    for i in xrange(6):
        with open('/home/fan/work/data/CityMomentum/10min_c80/D{}T{}.csv'.format((i-5+cur_t)/144,(i-5+cur_t)%144),'r') as f_data:
            for u_str,time_str,lat_str,lon_str in csv.reader(f_data):
                u = int(u_str)
                assert u in cluster
                if u not in cluster:
                    continue
                k = cluster[u]
                cur_time = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
                lat = float(lat_str)
                lon = float(lon_str)
                dis_lat = int( ( lat - 35.0 ) / 0.004 )
                dis_lon = int( ( lon - 139.0 ) / 0.005 )
                if u in lastloc:
                    dis_lat_pre,dis_lon_pre,pre_time = lastloc[u]
                    dt = cur_time - pre_time
                    idx = math.floor( dt / 60.0 ) + 1
                    if idx >= 60:
                        idx = 59
                    if (dis_lat_pre,dis_lon_pre) not in graph[k]:
                        graph[k][(dis_lat_pre,dis_lon_pre)] = {}

                    if (dis_lat,dis_lon) not in graph[k][(dis_lat_pre,dis_lon_pre)]:
                        hist = np.zeros(60,np.float)
                        hist[idx] += 1
                        graph[k][(dis_lat_pre,dis_lon_pre)][(dis_lat,dis_lon)] = (1,hist)
                    else:
                        n,hist = graph[k][(dis_lat_pre,dis_lon_pre)][(dis_lat,dis_lon)]
                        hist[idx] += 1
                        graph[k][(dis_lat_pre,dis_lon_pre)][(dis_lat,dis_lon)] = (n+1,hist)
                lastloc[u] = (dis_lat,dis_lon,cur_time)

    for k in xrange(K):
        for ori in graph[k]:
            for dst in graph[k][ori]:
                cnt,hist = graph[k][ori][dst]
                hist /= cnt
                graph[k][ori][dst] = cnt,hist

    print 'Build Graph Complete'

    with open('./simulated_c80/output_{}.csv'.format(cur_t),'w') as f:
        init_tstamp = time.mktime(time.strptime('2011-08-11 00:00:00','%Y-%m-%d %H:%M:%S'))
        init_tstamp += cur_t * 600 + 600
        term_tstamp = init_tstamp + 3600

        for u in lastloc:
            dis_lat,dis_lon,cur_time = lastloc[u]
            k = cluster[u]
            exp_time = init_tstamp

            ori_lat = dis_lat * 0.004 + 35.0 + 0.001 +  np.random.ranf()*0.002
            ori_lon = dis_lon * 0.005 + 139.0 + 0.00125 + np.random.ranf()*0.0025
            f.write('{},{},{},{},{}\n'.format(u,ori_lat,ori_lon,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(exp_time)),k))

            loopcnt = 0
            first_time = True
            while loopcnt < 20 and exp_time < term_tstamp:
                loopcnt += 1
                hop_hist_list = []
                hop_index = {}
                index = 0
                if (dis_lat,dis_lon) in graph[k]:
                    for (dis_lat_dst,dis_lon_dst) in graph[k][(dis_lat,dis_lon)]:
                        nhop = graph[k][(dis_lat,dis_lon)][(dis_lat_dst,dis_lon_dst)][0]
                        if (dis_lat_dst,dis_lon_dst) == (dis_lat,dis_lon):
                            nhop += 1
                        hop_hist_list.append(nhop)
                        hop_index[index] = (dis_lat_dst,dis_lon_dst)
                        index += 1
                    hop_hist = np.array(hop_hist_list,np.float)
                    hop_hist /= sum(hop_hist)
                    hop = np.random.multinomial(1,hop_hist).argmax()
                    hop_dis_lat,hop_dis_lon = hop_index[hop]
                    time_hist = graph[k][(dis_lat,dis_lon)][(hop_dis_lat,hop_dis_lon)][1]
                    hop_time = np.random.multinomial(1,time_hist).argmax()

                    # Because there is the blank range of (0,5)min
                    if first_time:
                        hop_time /= 2.0
                        first_time = False

                    exp_time += hop_time * 60
                    if exp_time >= term_tstamp:
                        exp_time -= hop_time * 60
                        continue

                    hop_lat = hop_dis_lat * 0.004 + 35.0 + 0.001 + np.random.ranf()*0.002
                    hop_lon = hop_dis_lon * 0.005 + 139.0 + 0.00125 + np.random.ranf()*0.0025

                    f.write('{},{},{},{},{}\n'.format(u,hop_lat,hop_lon,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(exp_time)),k))
                    dis_lat = hop_dis_lat
                    dis_lon = hop_dis_lon

if __name__ == '__main__':
    main()
