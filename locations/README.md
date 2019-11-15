# What is this repo?

This repo supports my main dissertation repo. It is intended to output all data pertaining to station location in a
single CSV file. It has two principle parts: location, and context. 

# Definitions

An alarming number of codes are used to refer to the UK rail network. They are described below. A great deal of effort
has been spent by a great many people ([e.g.](https://groups.google.com/forum/#!topic/openraildata-talk/cIGoODt26oE)) to bring these identifiers into one table. The current state-of-the-art (though
a proof-of-concept) has been developed by the Rail Delivery Group (RDG) and is available [here](https://wiki.openraildata.com/index.php?title=Locations_PoC).

#### Timing Point Location (TIPLOC)

* Relates to points used in deriving train schedules.
* Limited to seven characters.
* A station often has multiple TIPLOCs, where it consists on multiple groups of platforms on different lines.

#### Station Number (STANOX)

* Can refer to non-station locations such as sidings and junctions.
* First two digits are [the geographical area](https://wiki.openraildata.com/index.php?title=STANOX_Areas). These can be found
in stanox_areas.csv.
* Used in the Total Operations Processing System (TOPS).
* Supposed to be unique. In practice, some are re-used. Others are suffixed with a *, indicating a pseudo-STANOX, where a separate STANOX has yet to be issued.
* Numbers run broadly north-to-south; overseas areas have the lowest numbers.

#### Station Name (STANME)

* Describes a STANOX code.
* (Mostly) limited to 9 characters.
* Not unique.
* Often used in preference to the STANOX itself.

#### National Location Code (NLC)

* Six character codes (usually digits) which identify locations on the railway (e.g. stations, sidings, and booking offices).
* Used for retail purposes; play no role in train planning or running.
* Used in an accounting context to identify individual assets.
* Stations generally have NLCs ending in "00", so are often referred to by just the first four digits.
* First four digits refer to a location, and the last two a sub-location.
* The first digit indicates the location:
    * 0 is a 'group' station, pseudo-destination, London Underground station, or a London Fare Zone
    * 1 - 9 indicates a National Rail station, including self-service ticket machines
    * G, H, J, and K are usually Private Settlement locations (e.g. PlusBus destinations)
    * M and N are usually Irish stations.
    
#### Three-Letter Code (TLC)

* A.K.A. 3Alpha, CRS (Computer Reservation System), or NRS (National Reservation System) codes.
* NRS superseded CRS in 2004.
* Used primarily to identify stations, although some junctions and depots also have codes.
* Used on seat reservation labels.

#### NLC Description (NLCDESC / NLCDESC16)

* A description of the NLC. Either no limit (NLCDESC) or 16 characters (NLCDESC16).

# Sources

#### Location

Location data comes from the following sources:
* Open Rail Data Wiki (ORDW). Download [here](https://wiki.openraildata.com/index.php?title=File:TIPLOC_Eastings_and_Northings.xlsx.gz).
To use, extract the gzip file, and convert the .xlsx ("TIPLOC Eastings and Northings") to a .csv.
* Codes for Operations, Retail, & Planning - a Unified Solution (CORPUS). Download [here](http://datafeeds.networkrail.co.uk/ntrod/SupportingFileAuthenticate?type=CORPUS).
To use, extract the gzip file, and convert the "TIPLOCDATA" array in the .json ("out") to a .csv. 
* National Public Transport Access Nodes (NAPTAN). Download [here](http://naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv).
To use, extract the zip file, and use RailReferences.csv.
* A FOI request answered by Network Rail. Download [here](https://www.whatdotheyknow.com/request/521479/response/1266973/attach/5/01272%20GB%20TIPLOCs%20with%20Lat%20Long.xlsx).
To use, convert the .xlsx ("01272 GB TIPLOCs with Lat Long") to a .csv.

Those fields present are summarised below.

|                     | CORPUS | FOI | NAPTAN | ORDW |
|---------------------|--------|-----|--------|-----|
| STANOX              |    Y   |     |        |     |
| UIC                 |    Y   |     |        |     |
| 3ALPHA / CRS / NRS  |    Y   |     |    Y   |     |
| TIPLOC              |    Y   |  Y  |    Y   |  Y  |
| NLC                 |    Y   |     |        |     |
| NLCDESC             |    Y   |     |        |     |
| NLCDESC16           |    Y   |     |        |     |
| ATCO                |        |     |    Y   |     |
| EASTING, NORTHING   |        |     |    Y   |  Y  |
| LONGITUDE, LATITUDE |        |  Y  |        |     |
| NAME                |        |     |    Y   |  Y  |

#### Context

Station busy-ness data is released yearly by the Office for Road and Rail (ORR). The ORR is due to release data for the
2018 - 2019 financial year (the range of the primary dataset) in December 2019. For now, the data from the 2017 - 2018
financial year has been used. Download [here](https://dataportal.orr.gov.uk/media/1220/estimates-of-station-usage-2017-18.xlsx).

#### Information
* http://www.railwaycodes.org.uk/crs/CRS0.shtm
* https://wiki.openraildata.com/index.php?title=Identifying_Locations
* https://wiki.openraildata.com/index.php?title=NLC
* https://www.nationalrail.co.uk/stations_destinations/48541.aspx
* https://dataportal.orr.gov.uk/statistics/usage/estimates-of-station-usage/
