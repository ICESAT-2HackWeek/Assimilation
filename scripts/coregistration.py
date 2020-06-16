# this script was written by the Assimilation team as part of the ICESat-2 Hackweek 2020
# Team Members: Debmita Bandyopadhyay, Friedrich Knuth, Tian Li, Mike Wood, Whyjay Zheng

# Required packages
import gdal
import osr
import numpy as np
import pyproj
import rasterio
import pandas as pd
import geopandas as gpd

class reference_dem:

    def __init__(self,dem_file_path):
        self.dem_file_path = dem_file_path
        self.load_dem_from_path(dem_file_path)
        self.calculate_bounding_box(self.epsg)

    ##################################################################################
    # These are functions to initiate the DEM object and create the bounding box

    def load_dem_from_path(self,dem_file_path):
        if dem_file_path.endswith('.tif') or dem_file_path.endswith('.TIF'):
            ds = gdal.Open(dem_file_path)

            # read in the elevation array
            self.dem = np.array(ds.GetRasterBand(1).ReadAsArray())

            # create the x and y coordinate arrays
            transform = ds.GetGeoTransform()
            self.x = np.arange(transform[0],transform[0]+transform[1]*np.shape(self.dem)[1],transform[1])
            self.y = np.arange(transform[3], transform[3] + transform[5]*np.shape(self.dem)[0], transform[5])

            # get the EPSG code of the projection
            proj = osr.SpatialReference(wkt=ds.GetProjection())
            self.epsg = proj.GetAttrValue('AUTHORITY', 1)
            self.bbox_epsg = proj.GetAttrValue('AUTHORITY', 1)

            #close the file
            ds = None
        else:
            raise TypeError('DEM type not recognized')
    
    #defintition to transform coordinates from F. Paolo's tutorial
    def transform_coord(self,proj1, proj2, x, y):
        proj1 = pyproj.Proj("EPSG:"+str(proj1))
        proj2 = pyproj.Proj("EPSG:"+str(proj2))
        return pyproj.transform(proj1, proj2, x, y)


    def calculate_bounding_box(self,epsg):
        if epsg == self.bbox_epsg:
            if 'bbox' not in self.__dict__.keys():
                self.bbox = [float(self.x.min()),float(self.y.min()),float(self.x.max()),float(self.y.max())]
        else:
            bbox_corners = np.array([[self.x.min(),self.y.min()],
                                   [self.x.max(),self.y.min()],
                                   [self.x.max(),self.y.max()],
                                   [self.x.min(),self.y.max()]])
            t_y, t_x = self.transform_coord(int(self.epsg), epsg, bbox_corners[:,0], bbox_corners[:,1])
            self.bbox = [float(t_x.min()),float(t_y.min()),float(t_x.max()),float(t_y.max())]
            self.bbox_epsg = str(epsg)
    
    ##################################################################################
    # These are functions to compare ATLO6 data with the DEM data
    
    def colocate_icesat2_dem_points(self,icesat2_gdf):
        
        #Note: the GeoDataFrame should be in the same projection as the DEM
        #Check that this is correct from the output of the downloading/processing class
        
        rasterio_dataset = rasterio.open(self.dem_file_path)
        laser_hits = list(zip(icesat2_gdf['x'], icesat2_gdf['y']))
        dem_elevs = []
        for hit in rasterio_dataset.sample(laser_hits):
            dem_elevs.append(hit[0])
        comparison_df = list(zip(icesat2_gdf['x'], icesat2_gdf['y'], dem_elevs))
        comparison_df = pd.DataFrame.from_dict({'x':icesat2_gdf['x'],'y':icesat2_gdf['y'],'dem_elev': dem_elevs, 
                                        'is2_elev':icesat2_gdf['h'],'dem-is2':dem_elevs-icesat2_gdf['h']})
        
        comparison_df = comparison_df[comparison_df.dem_elev != rasterio_dataset.nodata]
        rasterio_dataset=None
        
        self.dem_is2_comparison = comparison_df
        