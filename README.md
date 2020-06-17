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
* Arctic Polar Region
* High-mountain Asia
* Pacific Northwestern United States

## Files
* `.gitignore`
<br> Globally ignored files by `git` for the project.
* `environment.yml`
<br> `conda` environment description needed to run this project.

## Installation
* `git clone https://github.com/ICESAT-2HackWeek/Assimilation.git`   
* `pip install -e Assimilation`

## Folders

### `contributors`
Each team member has it's own folder under contributors, where he/she can
work on their contribution. Having a dedicated folder for one-self helps to 
prevent conflicts when merging with master.

### `notebooks`
Notebooks that are considered delivered results for the project should go in
here.

### `scripts`
Helper utilities that are shared with the team

### Stand-up June 17th

What have we been working on?
* Enabled [netrc authentication](https://github.com/icesat2py/icepyx/pull/71) in collaboration with icepyx
* Created [simlib](https://github.com/ICESAT-2HackWeek/Assimilation/tree/master/simlib) library to host functions and classes
* Created methods to query NSIDC for metadata and send requests to the openaltimetry API ([example](https://github.com/ICESAT-2HackWeek/Assimilation/blob/master/contributors/icetianli/READ_ATL06.ipynb))
* Created methods for raster and point processing / analysis


What do we plan to do next?
* Create integrated workflow example using the simlib library for presentation tomorrow - Mike, Team
* Send requests to the openaltimetry in parallel - Tian, Friedrich
* Create quick plotting method using data returned from openaltimetry API prior to NSIDC download - Tian, Friedrich
* Create generic methods to mask / classify points using raster or polygon mask inputs - Debmita, Whyjay
* Create generic methods to mask reference DEMs using raster or polygon mask inputs - Friedrich, Mike
* Develop point gridding and interpolation methods - Whyjay

Blockers?
* Does anyone have a point of contact at openaltimetry to provide feedback?

