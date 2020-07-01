# Assimilation

## General Objectives
* Get comfortable working with ICESat-2 and DEM raster data in Python  
* Compare ICESat-2 data with various DEM raster data types (SAR, Lidar, Photogrammetry)
* Quantify errors when adjusting existing DEMs with ICESat-2 data over bare ground  
* Compare results from mid-latitude glaciers and polar glaciers  
* Use info in existing DEMs to interpolate/extrapolate between ICESat-2 points  

## Collaborators
Debmita Bandyopadhyay  
Friedrich Knuth  
Tian Li  
Mike Wood  
Whyjay Zheng  

## Team Lead
Whyjay Zheng

## Data Science Lead
Friedrich Knuth

## Study Sites
* **Pacific Northwestern United States** (showcased in the `notebooks` folder)

Potential future targets include Arctic Polar Region & High-mountain Asia.


## Files
* `.gitignore` - Globally ignored files by `git` for the project.
* `environment.yml` - `conda` environment description needed to run this project.
* `LICENSE` - license information.
* `setup.py` - configuration of `pip` installation.

## Installation
* `git clone https://github.com/ICESAT-2HackWeek/Assimilation.git`   
* `pip install -e Assimilation`

## Folders

### `contributors`
Each team member has it's own folder under here, where he/she work on their contribution.

### `figures`
Figures to be inserted in readme files or notebooks.

### `notebooks`
**Notebooks that are considered delivered results for the project.**

### `scripts`
Helper utilities that are not included in `simlib`.

### `simlib`
**Main library of the project.**

## Integrated Workflow

[Link to the project notebook](https://github.com/ICESAT-2HackWeek/Assimilation/blob/master/notebooks/Assimilation_presentation.ipynb)

* Overview of `simlib` library
  - Installation using `pip`
* Create a Reference DEM object
  - `reference_dem` object
  - Visualization
  - Extract bounding box information for downloading ICESat-2 data
* Locate ICESat-2 ATL06 data in the DEM domain
  - Query and download data from Open Altimetry with `OA_request` function
  - Query and download data from NSIDC with Icepyx
  - Parallel downloading enabled
  - Pre-filtering ATL06 data
  - Overlay ATL06 data on a basemap
* Compare the DEM with ATL06 over bare rock
  - Sample DEM elevations at ATL06 point locations
  - Classify land cover for each ATL06 point using input polygons (glacier outline)
  - Histogram and uncertatinty analysis
* Interpolating ATL06 data with DEM infomation
  - Compare results with different gridding algorithms
  - Generate profiles along any user-defined direction
  - Preliminary quality assessment

## Note from Stand-up June 17th

#### What have we been working on?
* Enabled [netrc authentication](https://github.com/icesat2py/icepyx/pull/71) in collaboration with icepyx
* Created [simlib](https://github.com/ICESAT-2HackWeek/Assimilation/tree/master/simlib) library to host functions and classes
* Created methods to query NSIDC for metadata and send requests to the OpenAltimetry API ([example](https://github.com/ICESAT-2HackWeek/Assimilation/blob/master/contributors/icetianli/READ_ATL06.ipynb))
* Created methods for raster and point processing / analysis


#### What do we plan to do next?
* Create integrated workflow example using the simlib library for presentation tomorrow - Mike, Team
* Send requests to the OpenAltimetry in parallel - Tian, Friedrich
* Create quick plotting method using data returned from OpenAltimetry API prior to NSIDC download - Tian, Friedrich
* Create generic methods to mask / classify points using raster or polygon mask inputs - Debmita, Whyjay
* Create generic methods to mask reference DEMs using raster or polygon mask inputs - Friedrich, Mike
* Develop point gridding and interpolation methods - Whyjay
* Develop DEM co-registration methods - Mike, Friedrich

<!-- #### Blockers?
* Does anyone have a point of contact at openaltimetry to provide feedback?

<img src="./figures/standup.png" width="400"> -->

