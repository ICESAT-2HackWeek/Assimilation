# this script was written by the Assimilation team as part of the ICESat-2 Hackweek 2020
# Team Members: Debmita Bandyopadhyay, Friedrich Knuth, Tian Li, Mike Wood, Whyjay Zheng

# Required packages
import gdal
import osr
import numpy as np
import pyproj
import rasterio
from rasterio.plot import show as rio_show
from rasterio.mask import mask
import geopandas as gpd

class reference_dem:

    def __init__(self,dem_file_path):
        self.load_dem_from_path(dem_file_path)
        self.calculate_bounding_box(self.epsg)
        self.path = dem_file_path

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
                self.bbox = [self.x.min(),self.y.min(),self.x.max(),self.y.max()]
        else:
            bbox_corners = np.array([[self.x.min(),self.y.min()],
                                   [self.x.max(),self.y.min()],
                                   [self.x.max(),self.y.max()],
                                   [self.x.min(),self.y.max()]])
            t_y, t_x = self.transform_coord(int(self.epsg), epsg, bbox_corners[:,0], bbox_corners[:,1])
            self.bbox = [t_x.min(),t_y.min(),t_x.max(),t_y.max()]
            self.bbox_epsg = str(epsg)
            
    def show(self, ax=None):
        if not ax:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplot()
        ds_rasterio = rasterio.open(self.path)
        rio_show(ds_rasterio, ax=ax)
        
    def ClippedByPolygon(self, polygon_shapefile):

        """
        Return all pixel values within a given polygon shapefile. 
        According to
        https://gis.stackexchange.com/questions/260304/extract-raster-values-within-shapefile-with-pygeoprocessing-or-gdal
        """
        # from rasterio import logging
        # log = logging.getLogger()
        # log.setLevel(logging.ERROR)

        from shapely.geometry import mapping

        shapefile = gpd.read_file(polygon_shapefile)
        geoms = shapefile.geometry.values
        # geometry = geoms[0] # shapely geometry
        # geoms = [mapping(geoms[0])] # transform to GeJSON format
        geoms = [mapping(geoms[i]) for i in range(len(geoms))]
        with rasterio.open(self.fpath) as src:
            out_image, out_transform = mask(src, geoms, crop=True, nodata=-9999.0)
            # The out_image result is a Numpy masked array
            # no_data = src.nodata
            # if no_data is None:
            # 	no_data = 0.0
            nodata = -9999.0
        # print(out_image)
        # print(out_image.data.shape)
        # print(out_image.data)
        try:
            clipped_data = out_image.data[0]
        except NotImplementedError:
            clipped_data = out_image[0]
        # PROBABLY HAVE TO CHANGE TO out_image[0] HERE
        # extract the valid values
        # and return them as a numpy 1-D array
        # return np.extract(clipped_data != nodata, clipped_data)
        return clipped_data

            