#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import math
import numpy as np

CACHE_LENGTH = 6
MAX_ITER = 30
K = 10
alpha = 0.5
beta = 0.1
gamma = 4000

poptime = dict({})
lastloc = dict({})
dataqueue = [dict({}) for i in xrange(CACHE_LENGTH)]
cluster = dict({})
theta = np.zeros(K,np.int32)
flowfield = [dict({}) for i in xrange(K)]

def loadfile(t,filename):
    dataqueue[t] = dict({})

    with open(filename,'r') as f:
        for u_str,time_str,lat_str,lon_str in csv.reader(f):
            u = int(u_str)
            lat = float( lat_str )
            lon = float( lon_str )
            tstamp = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            if u in lastloc:
                lat_pre,lon_pre,tstamp_pre = lastloc[u]
                dlat = ( lat - lat_pre )/0.004
                dlon = ( lon - lon_pre )/0.005
                vel = ( ( dlat**2 + dlon**2 )**0.5 )/( tstamp - tstamp_pre + 0.00001 )
                dis_lat_pre = int( ( lat_pre - 35.0 ) / 0.008 )
                dis_lon_pre = int( ( lon_pre - 139.0 ) / 0.010 )
                if vel < 0.006:
                    if lat <= lat_pre and lon < lon_pre:
                        if lon - lon_pre >= lat - lat_pre:
                            index = -1
                        else:
                            index = -2
                    elif lat > lat_pre and lon <= lon_pre:
                        if lon - lon_pre < - ( lat - lat_pre ):
                            index = -3
                        else:
                            index = -4
                    elif lat >= lat_pre and lon > lon_pre:
                        if lon - lon_pre < lat - lat_pre:
                            index = -5
                        else:
                            index = -6
                    else:
                        if lon - lon_pre >= - ( lat - lat_pre ):
                            index = -7
                        else:
                            index = -8
                elif vel < 0.025:
                    if lat <= lat_pre and lon < lon_pre:
                        if lon - lon_pre >= lat - lat_pre:
                            index = 1
                        else:
                            index = 2
                    elif lat > lat_pre and lon <= lon_pre:
                        if lon - lon_pre < - ( lat - lat_pre ):
                            index = 3
                        else:
                            index = 4
                    elif lat >= lat_pre and lon > lon_pre:
                        if lon - lon_pre < lat - lat_pre:
                            index = 5
                        else:
                            index = 6
                    else:
                        if lon - lon_pre >= - ( lat - lat_pre ):
                            index = 7
                        else:
                            index = 8
                else:
                    if lat <= lat_pre and lon < lon_pre:
                        if lon - lon_pre >= lat - lat_pre:
                            index = 9
                        else:
                            index = 10
                    elif lat > lat_pre and lon <= lon_pre:
                        if lon - lon_pre < - ( lat - lat_pre ):
                            index = 11
                        else:
                            index = 12
                    elif lat >= lat_pre and lon > lon_pre:
                        if lon - lon_pre < lat - lat_pre:
                            index = 13
                        else:
                            index = 14
                    else:
                        if lon - lon_pre >= - ( lat - lat_pre ):
                            index = 15
                        else:
                            index = 16
                if u not in dataqueue[t]:
                    dataqueue[t][u] = [((dis_lat_pre,dis_lon_pre),index)]
                else:
                    dataqueue[t][u].append(((dis_lat_pre,dis_lon_pre),index))
            poptime[u] = t
            lastloc[u] = (lat,lon,tstamp)

def random_initialize():
    for t in xrange(CACHE_LENGTH):
        for u in dataqueue[t]:
            if u not in cluster:
                k = np.random.randint(K)
                cluster[u] = k
                theta[k] += 1

def build_flowfield(t):
    for u in dataqueue[t]:
        if u not in cluster:
            k = np.random.randint(K)
            cluster[u] = k
            theta[k] += 1
        k = cluster[u]
        for v in dataqueue[t][u]:
            p_beg,i_end = v
            if p_beg not in flowfield[k]:
                flowfield[k][p_beg] = np.zeros(18,np.float)
            if i_end < 0:
                flowfield[k][p_beg][0] += 0.8
                flowfield[k][p_beg][-i_end] += 0.2
            elif i_end <= 8:
                flowfield[k][p_beg][0] += 0.05
                flowfield[k][p_beg][i_end%8+1] += 0.15
                flowfield[k][p_beg][i_end] += 0.6
                if i_end == 1:
                    flowfield[k][p_beg][8] += 0.15
                else:
                    flowfield[k][p_beg][i_end-1] += 0.15
                flowfield[k][p_beg][i_end+8] += 0.05
            else:
                flowfield[k][p_beg][i_end-8] += 0.1
                if i_end == 16:
                    flowfield[k][p_beg][9] += 0.15
                else:
                    flowfield[k][p_beg][i_end+1] += 0.15
                flowfield[k][p_beg][i_end] += 0.6
                if i_end == 9:
                    flowfield[k][p_beg][16] += 0.15
                else:
                    flowfield[k][p_beg][i_end-1] += 0.15
            flowfield[k][p_beg][17] += 1.0

def removeoneuser(u):
    theta[cluster[u]] -= 1
    for t in xrange(CACHE_LENGTH):
        if u not in dataqueue[t]:
            continue
        k = cluster[u]
        for v in dataqueue[t][u]:
            p_beg,i_end = v
            if i_end < 0:
                flowfield[k][p_beg][0] -= 0.8
                flowfield[k][p_beg][-i_end] -= 0.2
            elif i_end <= 8:
                flowfield[k][p_beg][0] -= 0.05
                flowfield[k][p_beg][i_end%8+1] -= 0.15
                flowfield[k][p_beg][i_end] -= 0.6
                if i_end == 1:
                    flowfield[k][p_beg][8] -= 0.15
                else:
                    flowfield[k][p_beg][i_end-1] -= 0.15
                flowfield[k][p_beg][i_end+8] -= 0.05
            else:
                flowfield[k][p_beg][i_end-8] -= 0.1
                if i_end == 16:
                    flowfield[k][p_beg][9] -= 0.15
                else:
                    flowfield[k][p_beg][i_end+1] -= 0.15
                flowfield[k][p_beg][i_end] -= 0.6
                if i_end == 9:
                    flowfield[k][p_beg][16] -= 0.15
                else:
                    flowfield[k][p_beg][i_end-1] -= 0.15
            flowfield[k][p_beg][17] -= 1.0
            if flowfield[k][p_beg][17] < 0.000001:
                del flowfield[k][p_beg]

def calprobablity(u,k):
    p = 0.0
    for t in xrange(CACHE_LENGTH):
        if u not in dataqueue[t]:
            continue
        for v in dataqueue[t][u]:
            p_beg,i_end = v
            if p_beg in flowfield[k]:
                if i_end < 0:
                    p += 0.8 * ( math.log( flowfield[k][p_beg][0] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    p += 0.2 * ( math.log( flowfield[k][p_beg][-i_end] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                elif i_end <= 8:
                    p += 0.05 * ( math.log( flowfield[k][p_beg][0] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    p += 0.15 * ( math.log( flowfield[k][p_beg][i_end%8+1] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    p += 0.6 * ( math.log( flowfield[k][p_beg][i_end] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    if i_end == 1:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][8] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    else:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][i_end-1] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    p += 0.05 * ( math.log( flowfield[k][p_beg][i_end+8] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                else:
                    p += 0.10 * ( math.log( flowfield[k][p_beg][i_end-8] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    if i_end == 16:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][9] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    else:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][i_end+1] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    p += 0.6 * ( math.log( flowfield[k][p_beg][i_end] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    if i_end == 9:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][16] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
                    else:
                        p += 0.15 * ( math.log( flowfield[k][p_beg][i_end-1] + alpha ) - math.log( flowfield[k][p_beg][17] + 17*alpha ) )
            else:
                p += beta
    p = math.exp(p)
    p *= theta[k] + gamma
    return p

def conditional_distribution(u):
    p_list = [calprobablity(u,k) for k in xrange(K)]
    return np.array(p_list)

def sample_index(p):
    p /= sum(p)
    return np.random.multinomial(1,p).argmax()

def updateoneuser(u,k):
    for t in xrange(CACHE_LENGTH):
        if u not in dataqueue[t]:
            continue
        for v in dataqueue[t][u]:
            p_beg,i_end = v
            if p_beg not in flowfield[k]:
                flowfield[k][p_beg] = np.zeros(18,np.float)
            if i_end < 0:
                flowfield[k][p_beg][0] += 0.8
                flowfield[k][p_beg][-i_end] += 0.2
            elif i_end <= 8:
                flowfield[k][p_beg][0] += 0.05
                flowfield[k][p_beg][i_end%8+1] += 0.15
                flowfield[k][p_beg][i_end] += 0.6
                if i_end == 1:
                    flowfield[k][p_beg][8] += 0.15
                else:
                    flowfield[k][p_beg][i_end-1] += 0.15
                flowfield[k][p_beg][i_end+8] += 0.05
            else:
                flowfield[k][p_beg][i_end-8] += 0.1
                if i_end == 16:
                    flowfield[k][p_beg][9] += 0.15
                else:
                    flowfield[k][p_beg][i_end+1] += 0.15
                flowfield[k][p_beg][i_end] += 0.6
                if i_end == 9:
                    flowfield[k][p_beg][16] += 0.15
                else:
                    flowfield[k][p_beg][i_end-1] += 0.15
            flowfield[k][p_beg][17] += 1.0

def clustering():
    for n in xrange(MAX_ITER):
        print 'Iteration {}'.format(n)
        for u in cluster:
            removeoneuser(u)
            p = conditional_distribution(u)
            k = sample_index(p)
            cluster[u] = k
            theta[k] += 1
            updateoneuser(u,k)

def popslice(t):
    # Remove one slice
    for u in dataqueue[t]:
        if poptime[u] == t:
            removeoneuser(u)
            del poptime[u]
            del lastloc[u]
            del cluster[u]

def main():
    # Initialize
    for t in xrange(CACHE_LENGTH):
        loadfile(t,'/home/fan/work/data/CityMomentum/10min_newyear/D0T{}.csv'.format(t))
    random_initialize()
    for t in xrange(CACHE_LENGTH):
        build_flowfield(t)
    clustering()

    print 'Initialization Complete'

    # Online updating
    for dt in xrange(CACHE_LENGTH,144*2):
        d = dt/144
        t = dt%144
        popslice(dt%CACHE_LENGTH)
        loadfile(dt%CACHE_LENGTH,'/home/fan/work/data/CityMomentum/10min_newyear/D{}T{}.csv'.format(d,t))
        build_flowfield(dt%CACHE_LENGTH)
        clustering()
        # Output
        with open('./newyear_clustering/usercluster_{}.csv'.format(dt),'w') as f:
            for u in cluster:
                f.write('{},{}\n'.format(u,cluster[u]))
        print '{} Complete'.format(dt)

if __name__ == '__main__':
    main()
