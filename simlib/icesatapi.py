# utility modules
import glob
import os
import sys
import re
import requests
import numpy as np
import pandas as pd
from itertools import compress
import simlib.config as cn

def grid_bbox(bbox, binsize = 5):
    """
    Split bounding box into smaller grids if latitude/longitude range exceed the default 5 degree limit of OpenAltimetry 
    """
        
    lonmin = bbox[0]
    latmin = bbox[1]
    lonmax = bbox[2]
    latmax = bbox[3]

    lonx = np.arange(lonmin, lonmax + binsize, binsize)
    laty = np.arange(latmin, latmax + binsize, binsize) 
    lonxv, latyv = np.meshgrid(lonx, laty)
    
    ydim, xdim = lonxv.shape 

    bbox_list = []
    for i in np.arange(0,ydim-1): 
        for j in np.arange(0,xdim-1):
            # iterate grid for bounding box
            bbox_ij = [lonxv[i,j], latyv[i,j], lonxv[i+1,j+1], latyv[i+1,j+1]]
            
            if bbox_ij[2] > lonmax:
                bbox_ij[2] = lonmax

            if bbox_ij[3] > latmax:
                bbox_ij[3] = latmax

            bbox_list.append(bbox_ij)
            
    return bbox_list

def file_meta(filelist,bbox):
    """
    Derive metadata from filename
    Input:
        fname: ATL06 file name
        bbox: bbox of the DEM
    Output:
        rgt
        ftime: format (yyyy-mm-dd)
        cycle
        bbox
    """
    file_re=re.compile('ATL06_(?P<date>\d+)_(?P<rgt>\d\d\d\d)(?P<cycle>\d\d)(?P<region>\d\d)_(?P<release>\d\d\d)_(?P<version>\d\d).h5')
    
    para_lists = [] # list of parameters for API query
    
    for fname in filelist:
        
        temp=file_re.search(fname)
        rgt = temp['rgt'].strip("0")
        cycle = temp['cycle'].strip("0")
        f_date = temp['date']
        ftime = f_date[:4] + '-' + f_date[4:6] + '-' + f_date[6:8]
        
        paras = [rgt, ftime, cycle, bbox]
        para_lists.append(paras)
    
    return para_lists

def OA_request(paralist, product = 'atl06'):
    """
    Request data from OpenAltimetry based on API
    Inputs:
        paralist: [trackId, Date, cycle, bbox]
            trackId: RGT number
            beamlist: list of beam number
            cycle: cycle number
            bbox: DEM bounding box
        product: ICESat-2 product
    Output:
        track_df: dataframe for all beams of one RGT
    """
    points = [] # store all beam data for one RGT
    trackId,Date,cycle,bbox = paralist[0], paralist[1], paralist[2], paralist[3]
    # iterate all six beams 
    for beam in cn.beamlist:
        # Generate API
        payload =  {'product':product,
                    'endDate': Date,
                    'minx':str(bbox[0]),
                    'miny':str(bbox[1]),
                    'maxx':str(bbox[2]),
                    'maxy':str(bbox[3]),
                    'trackId': trackId,
                    'beamName': beam,
                    'outputFormat':'json'}
        
        # request OpenAltimetry
        r = requests.get(cn.base_url, params=payload)
        
        # get elevation data
        elevation_data = r.json()
        
        # length of file list
        file_len = len(elevation_data['data'])
        
        # file index satifies aqusition time from data file
        idx = [elevation_data['data'][i]['date'] == Date for i in np.arange(file_len)]
        
        # get data we need
        beam_data = list(compress(elevation_data['data'], idx)) 
        
        if not beam_data:
            continue
        
        # elevation array
        beam_elev = beam_data[0]['beams'][0]['lat_lon_elev']

        if not beam_elev: # check if no data 
            continue # continue to next beam  

        for p in beam_elev:
            points.append({
                'lat': p[0],
                'lon': p[1],
                'h': p[2],
                'beam': beam,
                'cycle': cycle,
                'time' : Date}
            )
    
    track_df = pd.DataFrame.from_dict(points)
    
    return track_df