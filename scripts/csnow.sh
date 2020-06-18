#! /bin/bash

ls $1 | while read x; do \
gdal_translate NETCDF:"$1/$x":snd_upd tmp.tif -co TILED=YES; \
gdalmdimtranslate tmp.tif tmp2.tif -co TILED=YES -array "band=1,transpose=[1,0],view=[::-1,::-1]"; \
echo "<PAMDataset>
  <Metadata domain="GEOLOCATION">
    <MDI key="LINE_OFFSET">0</MDI>
    <MDI key="LINE_STEP">1</MDI>
    <MDI key="PIXEL_OFFSET">0</MDI>
    <MDI key="PIXEL_STEP">1</MDI>
    <MDI key="SRS">EPSG:4326</MDI>
    <MDI key="X_BAND">1</MDI>
    <MDI key="X_DATASET">NETCDF:"csnow/$x":lon</MDI>
    <MDI key="Y_BAND">1</MDI>
    <MDI key="Y_DATASET">NETCDF:"csnow/$x":lat</MDI>
  </Metadata>
</PAMDataset>" > $1/tmp2.tif.aux.xml; \
gdalwarp tmp2.tif $1/$x.tif -overwrite -co TILED=YES; \
rm -f $1/tmp.tif $1/tmp2.tif ; done