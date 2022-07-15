# how to use

## opentopodata

* had to download the data from Nasa's [here](https://e4ftl01.cr.usgs.gov/ASTT/ASTGTM.003/2000.03.01/ASTGTMV003_N48W067.zip)
* follow instruction [here](https://www.opentopodata.org/datasets/aster/) about how to install opentodata locally. Section "Adding 30m aster to opendata" (there are low limits on the open online api)
* to install opentodata locally, follow [these instructions](https://www.opentopodata.org/), section `Host your own`.

## usage
* cd /opendata && `make run` to launch the local server
* then have your URL in python make calls to `http://localhost:5000/`