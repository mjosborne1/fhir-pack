# How to build the environment for this script
   *  In your development/scripts folder 
   * `git clone https://github.com/mjosborne1/fhir-pack`
   * `cd fhir-pack`
   * `pip install -r requirements.txt`
   * `pip install fhirclient`   (In case it doesn't install from the requirements file)
   * `virtualenv env`
   * `source env/bin/activate`
   * open the fhirpack folder in your development environment (IDE) of choice e.g. VS Code
   * in the root folder of fhir-pack create a new file `.env`


## Get your client credentials for NCTS
   1. Log into https://www.healthterminologies.gov.au/
   1. Click on `Clients`
   1. If you have system client credentials, copy these to the .env file in the root fhir-pack folder
   ![image](env-file.png ".env")

## run the script
   * open a cmd prompt in the fhir-pack folder
   * `python main.py`
   * Some defaults are set that may not work for you so check the arguments by running `python main.py --help`
```
usage: main.py [-h] [-o OUTDIR] [-t TMPDIR] [-p PACKAGE_NAME] [-v PACKAGE_VERSION] [-r RELEASE]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        ouput root dir for npm packages
  -t TMPDIR, --tmpdir TMPDIR
                        tmp dir for downloaded bundles
  -p PACKAGE_NAME, --package_name PACKAGE_NAME
                        npm package name
  -v PACKAGE_VERSION, --package_version PACKAGE_VERSION
                        npm package version   x.y.z
  -r RELEASE, --release RELEASE
                        NCTS release version  YYYYMMDD
```

Examples:
On windows: 
   `python main.py -o "C:\DATA\npm"  -t "C:\TEMP\fhir-pack" -p "healthterminologies.gov.au" -v "4.0.1" -r "20240331"`
On Mac / Linux:
   `python main.py -o "~/data/npm" -t "/tmp/fhir-pack" -p "healthterminologies.gov.au" -v "4.0.1" -r "20240331"`
