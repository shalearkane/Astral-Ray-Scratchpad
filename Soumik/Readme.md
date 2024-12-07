# Flow

## Structure of Code
### Constants
Constains list of
- MongoDB Collections
- Output Directories
- Redis Queues
- Server URIs
### Criterion
Has code for list of criterias for CLASS file selection
- Geotail
- GOES Solar Flare
- Photon Count
- Illumination (superceded by Photon Count)

All of these takes the FITs file or datetime as input.
### GDL
Has code for extracting data out of XSM PHA files
- Raw Energy Bins -> Extracts Flux vs Energy w.r.t Time data from PHA files using OSPEX (using GDL interpreter instead of IDL)
- Flux From Raw Energy Bins -> Reads the raw data from OSPEX output and creates Pandas Dataframe to aid in filtering data

### Helpers
This contains files for various independent functionality
- **Combine Fits** -> combines a list of FITs file given a functionality
- **Download File** -> get a file from file server after checking if it is not present in download location
- **Pre-Process** -> sort dataframe and remove duplicates given a key
- **Query CLASS** -> queries MongoDB for various types of requests e.g. all class files that covers a certain latitude and longitude, returns list of docs
- **Query XSM** -> queries XSM for various types of requests e.g. all xsm files that covers a given time range
- **Utilities** -> datetime conversion functions
- **Visible Peaks** -> function to get peaks of elements given a CLASS fits file
- **XSet** -> settings for running XSPEC e.g. increasing threads and removing logs

### Model
- **Handcrafted** -> Our custom model using XSPEC for fitting
- **Model_Generic** -> X2Abund model with tweaks that takes only a CLASS Fits file as input
- **Model_X2** -> X2Abund Model

### Plot
- **Quadrilaterals** -> Plots to a patches of land to a file
- **PlotAbundances** -> Plot the raw data outputs by xrf and the predicted abundances by our model.

### Scatter
- **Scatter From Incident** -> Calculates Scattered Spectrum from Solar Incident spectrum based on ffast data and outputs to a CSV
- **Scatter From Incident Alt** -> Same as before but by using a fixed piecewise continuous function
- **PreProcess** -> Clean the output
- **Generate Fits** -> Creates the Table Model file from the spectrum CSV

### Scripts
- **CSV Split** -> split input csv files for parallel processing
- **Equidistant Points** -> generates points for sampling using Fibonacci Sphere Algorithm
- **Get Intersections** -> calculates intersections between land-patches

## Server
- **Redis Check Queue** -> listens to a redis *check* queue, checks if given fits file can be used for processing, output to *process* queue
- **Redis Process Queue** -> listens to a redis *process* queue, calculates xrf line intensities and fit parameters
- **Redis Test** -> for testing the redis processes

## Calculations
### Data Prepocessing
Applies to all files, data updated to MongoDB
- **Process-Flare-Classes** -> assigns solar flare class to each CLASS file (if present)
- **Process-Photon-Count** -> assigns photon count to each file
- **Process-Add-Visible-Peak** -> assigns visible peaks data to each file

### Final Calculations
Applies to only filtered files based on given criteria
- **Process Fibonacci Abundance** -> calculates xrf line intensities of each generated latitude longitude in the following way
    - Fetched job from MongoDB on which latitude is to be calculated
    - Fetches and combines all the fits files at a given latitude longitudes using weighted average, weight being the photon count of each file
    - Calculates visible peaks
    - Calculates XRF line intensities for the combine fits
    - Outputs to MongoDB

- **Process-Combined-Fits** -> superceded by the above file. used to combine fits files for all given latitude and longitude ranges for distributed process