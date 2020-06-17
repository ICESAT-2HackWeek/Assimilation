from pathlib import Path
import pyproj
from astropy.time import Time
import h5py
import numpy as np

def gps2dyr(time):
    """Converte GPS time to decimal years."""
    return Time(time, format='gps').decimalyear


def orbit_type(time, lat, tmax=1):
    """Separate tracks into ascending and descending.
    
    Defines tracks as segments with time breaks > tmax,
    and tests whether lat increases or decreases w/time.
    """
    tracks = np.zeros(lat.shape)  # generate track segment
    tracks[0:np.argmax(np.abs(lat))] = 1  # set values for segment
    is_asc = np.zeros(tracks.shape, dtype=bool)  # output index array

    # Loop trough individual secments
    for track in np.unique(tracks):
    
        i_track, = np.where(track == tracks)  # get all pts from seg
    
        if len(i_track) < 2: continue
    
        # Test if lat increases (asc) or decreases (des) w/time
        i_min = time[i_track].argmin()
        i_max = time[i_track].argmax()
        lat_diff = lat[i_track][i_max] - lat[i_track][i_min]
    
        # Determine track type
        if lat_diff > 0:  is_asc[i_track] = True
    
    return is_asc


def transform_coord(proj1, proj2, x, y):
    """Transform coordinates from proj1 to proj2 (EPSG num).

    Example EPSG projections:
        Geodetic (lon/lat): 4326
        Polar Stereo AnIS (x/y): 3031
        Polar Stereo GrIS (x/y): 3413
    """
    # Set full EPSG projection strings
    proj1 = pyproj.Proj("+init=EPSG:"+str(proj1))
    proj2 = pyproj.Proj("+init=EPSG:"+str(proj2))
    return pyproj.transform(proj1, proj2, x, y)  # convert

    
def segment_diff_filter(dh_fit_dx, h_li, tol=2):
    """ Coded by Ben Smith @ University of Washington """
    dAT = 20.0

    if h_li.shape[0] < 3:
        mask = np.ones_like(h_li, dtype=bool)

        return mask

    EPplus = h_li + dAT * dh_fit_dx
    EPminus = h_li - dAT * dh_fit_dx

    segDiff = np.zeros_like(h_li)
    segDiff[0:-1] = np.abs(EPplus[0:-1] - h_li[1:])
    segDiff[1:] = np.maximum(segDiff[1:], np.abs(h_li[0:-1] - EPminus[1:]))

    mask = segDiff < tol

    return mask

def read_atl06(fname, epsg, outdir='data', bbox=None):
    """Read one ATL06 file and output 6 reduced files. 
    
    Extract variables of interest and separate the ATL06 file 
    into each beam (ground track) and ascending/descending orbits.
    """

    # Each beam is a group
    group = ['/gt1l', '/gt1r', '/gt2l', '/gt2r', '/gt3l', '/gt3r']

    # Loop trough beams
    for k, g in enumerate(group):
    
        #-----------------------------------#
        # 1) Read in data for a single beam #
        #-----------------------------------#
        
        data = {}
    
        try:
            # Load vars into memory (include as many as you want)
            with h5py.File(fname, 'r') as fi:
                
                data['lat'] = fi[g+'/land_ice_segments/latitude'][:]
                data['lon'] = fi[g+'/land_ice_segments/longitude'][:]
                data['h_li'] = fi[g+'/land_ice_segments/h_li'][:]
                data['s_li'] = fi[g+'/land_ice_segments/h_li_sigma'][:]
                data['t_dt'] = fi[g+'/land_ice_segments/delta_time'][:]
                data['q_flag'] = fi[g+'/land_ice_segments/atl06_quality_summary'][:]
                data['s_fg'] = fi[g+'/land_ice_segments/fit_statistics/signal_selection_source'][:]
                data['snr'] = fi[g+'/land_ice_segments/fit_statistics/snr_significance'][:]
                data['h_rb'] = fi[g+'/land_ice_segments/fit_statistics/h_robust_sprd'][:]
                data['dac'] = fi[g+'/land_ice_segments/geophysical/dac'][:]
                data['f_sn'] = fi[g+'/land_ice_segments/geophysical/bsnow_conf'][:]
                data['dh_fit_dx'] = fi[g+'/land_ice_segments/fit_statistics/dh_fit_dx'][:]
                data['tide_earth'] = fi[g+'/land_ice_segments/geophysical/tide_earth'][:]
                data['tide_load'] = fi[g+'/land_ice_segments/geophysical/tide_load'][:]
                data['tide_ocean'] = fi[g+'/land_ice_segments/geophysical/tide_ocean'][:]
                data['tide_pole'] = fi[g+'/land_ice_segments/geophysical/tide_pole'][:]
                
                rgt = fi['/orbit_info/rgt'][:]                           # single value
                t_ref = fi['/ancillary_data/atlas_sdp_gps_epoch'][:]     # single value
                beam_type = fi[g].attrs["atlas_beam_type"].decode()      # strong/weak (str)
                spot_number = fi[g].attrs["atlas_spot_number"].decode()  # number (str)
                
        except:
            print('skeeping group:', g)
            print('in file:', fname)
            continue
            
        #---------------------------------------------#
        # 2) Filter data according region and quality #
        #---------------------------------------------#
        
        # Select a region of interest
        if bbox:
            lonmin, latmin, lonmax, latmax = bbox
            bbox_mask = (data['lon'] >= lonmin) & (data['lon'] <= lonmax) & \
                        (data['lat'] >= latmin) & (data['lat'] <= latmax)
        else:
            bbox_mask = np.ones_like(data['lat'], dtype=bool)  # get all
            
        # Compute segment difference mask
        diff_mask = segment_diff_filter(data['dh_fit_dx'], data['h_li'], tol=2)
            
        # Only keep good data (quality flag + threshold + bbox)
        mask = (data['q_flag'] == 0) & (np.abs(data['h_li']) < 10e3) & (bbox_mask == 1) & diff_mask
        
        # If no data left, skeep
        if not any(mask): continue
        
        # Update data variables
        for k, v in data.items(): data[k] = v[mask]
            
        #----------------------------------------------------#
        # 3) Convert time, separate tracks, reproject coords #
        #----------------------------------------------------#
        
        # Time in GPS seconds (secs sinde Jan 5, 1980)
        t_gps = t_ref + data['t_dt']

        # Time in decimal years
        t_year = gps2dyr(t_gps)

        # Determine orbit type
        is_asc = orbit_type(t_year, data['lat'])
        
        # Geodetic lon/lat -> Polar Stereo x/y
        x, y = transform_coord(4326, epsg, data['lon'], data['lat'])
        
        data['x'] = x
        data['y'] = y
        data['t_gps'] = t_gps
        data['t_year'] = t_year
        data['is_asc'] = is_asc
        
        #-----------------------#
        # 4) Save selected data #
        #-----------------------#
        
        # Define output dir and file
        outdir = Path(outdir)    
        fname = Path(fname)
        outdir.mkdir(exist_ok=True)
        outfile = outdir / fname.name.replace('.h5', '_' + g[1:] + '.h5')
        
        # Save variables
        with h5py.File(outfile, 'w') as fo:
            for k, v in data.items(): fo[k] = v
            print('out ->', outfile)


def read_h5(fname, vnames=None):
    “”"Read hdf5 file and return all variables”“”
    with h5py.File(fname, ‘r’) as f:
        if not vnames:
            vnames = [key for key in f.keys()]
        return np.column_stack([f[v][()] for v in vnames]), vnames
    
    
def points_in_polygon(points_geometry, shp_filename):
    # points_geometry: N-by-2 np array defining the geometry of points
    # shp_filename: (multi-)polygon shapefile name 
    # Both datasets should have the SAME CRS!

    # return: np mask array showing where the targeted points are.

    # import logging
    # logging.basicConfig(level=logging.WARNING)
    import geopandas as gpd
    from shapely.geometry import Point
    # from shapely.geometry import mapping

    shapefile = gpd.read_file(shp_filename)
    poly_geometries = [shapefile.loc[i]['geometry'] for i in range(len(shapefile))]
    pt_geometries = [Point(xy) for xy in zip(points_geometry[:, 0], points_geometry[:, 1])]
    pt_gs = gpd.GeoSeries(pt_geometries)

    idx = None
    for single_poly in poly_geometries:
        if idx is None:
            idx = pt_gs.within(single_poly)
        else:
            tmp = pt_gs.within(single_poly)
            idx = np.logical_or(idx, tmp)

    return idx