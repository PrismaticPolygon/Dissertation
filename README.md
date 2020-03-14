# Dates

The 2018 - 2019 UK financial year runs from 1/4/2018 to 3/31/2019.
This period was chosen for two main reasons:

1. It is the period covered by ORR's station usage statistics.
2. It is the period covered by NR's historic delay attribution data.

It imposes only a slight overhead on the weather data-set, which is released in calendar years. The primary data-set is
released in days and so is unaffected

https://pbpython.com/categorical-encoding.html

## TODO:

* Convert cyclical variables into unit circle equivalents ([here](http://blog.davidkaleko.com/feature-engineering-cyclical-features.html)). That said,
one-hot encoding time features often works better than

# Data

There are eight message types:

| Type | Description |
|------|-------------|
|0001|[Train activation](https://wiki.openraildata.com/index.php?title=Train_Activation)|
|0002|[Train cancellation](https://wiki.openraildata.com/index.php?title=Train_Cancellation)|
|0003|[Train movement](https://wiki.openraildata.com/index.php?title=Train_Movement)|
|0004|Not used in production|
|0005|[Train reinstatement](https://wiki.openraildata.com/index.php?title=Train_Reinstatement)|
|0006|[Change of origin](https://wiki.openraildata.com/index.php?title=Change_of_Origin)|
|0007|[Change of identity](https://wiki.openraildata.com/index.php?title=Change_of_Identity)|
|0008|[Change of location](https://wiki.openraildata.com/index.php?title=Change_of_Location)|

We are primarily interested in 0003.

### Fields

Fields can be found [here](https://wiki.openraildata.com/index.php?title=Train_Movement).

| Field                  | Description                                                                                                                    |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| event_type             | ARRIVAL or DEPARTURE                                                                                                    |
| gbtt_timestamp         | The planned GBTT (passenger) datetime that the event was due to happen at                                                      |
| original_loc_stanox    | If the location has been revised, the STANOX of the location in the schedule at activation time                                |
| planned_timestamp      | The planned date and time that this event was due to happen at this location                                                   |
| timetable_variation    | The number of minutes variation from the scheduled time at this location. Off-route reports will contain '0'                   |
| original_loc_timestamp | The planned time associated with the original location                                                                         |
| current_train_id       | If a train has had its identity changed, the current 10-character unique identity for this train                               |
| delay_monitoring_point | True if a delay monitoring point. Off-route reports are False                                                    |
| next_report_run_time   | The running time to the next location                                                                                          |
| reporting_stanox       | The STANOX of the location that generated this report. Set to 00000 for manual and off-route reports                           |
| actual_timestamp       | The date and time that this event happened at the location                                                                     |
| correction_ind         | True if this report is a correction of a previous point                                                                        |
| event_source           | AUTOMATIC from SMART, or MANUAL from TOPS or TRUST SDR                                                                         |
| train_file_address     | The TOPS train file address, if applicable                                                                                     |
| platform               | Two characters (including a space for a single character) or blank if the movement report is associated with a platform number |
| division_code          | Operating company ID as per TOC codes                                                                                          |
| train_terminated       | True if the train has completed its journey                                                                                    |
| train_id               | The 10-character unique identity for this train at TRUST activation time                                                       |
| offroute_ind           | False if this report is for a location in the schedule                                                                         |
| variation_status       | ON TIME, EARLY, LATE, or OFF ROUTE                                                                                             |
| train_service_code     | Train service code as per schedule                                                                                             |
| toc_id                 | Operating company ID as per TOC codes                                                                                          |
| loc_stanox             | The STANOX of the location at which this event happened                                                                        |
| auto_expected          | True if an automatic report is expected for this location                                                                      |
| direction_ind          | For automatic reports, either UP or DOWN                                                                                       |
| route                  | A single character (or blank) indicating the exit route from this location                                                     |
| planned_event_type     | ARRIVAL, DEPARTURE, or DESTINATION                                                                                             |
| next_report_stanox     | The STANOX of the location at which the next report for this train is due                                                      |
| line_ind               | A single character or blank depending on the line that the train is travelling on                                              |

### Engineered features

Several features can be engineered from just this data.
* STANOX area


### TRUST ID

A TRUST ID is a 10-character unique identifier (described [here](https://wiki.openraildata.com/index.php/Train_Activation#Body)) 
of the form AABBBCDEE. Several features can be engineered from the ID:
* AA is the first two digits of the origin STANOX (the area the train originated).
* BBBB is the signalling ID (headcode) used with data feeds to represent the train.
* C is the TSPEED value of the train. See below.
* D is the call code of the train. See below.
* EE is the day of the month on which the trian originated.

##### Train status code (TSPEED)

There are 4 possible values:

|Status|Code|
|------|----|
|Passenger and parcels in WTT|M - O|
|Freight trains in WTT|C - G|
|Trips and agreed pathways|A, B, H - L, P - Z|
|Special trains (freight or passenger)|0 - 9| 

##### Call code

A call code is a single alphanumeric digit that indicates when a train departed from its origin. Every character
0 - 6, A - Z, 7 - 9, represents an hour. This can be used to estimate how long the train has been travelling for,
and thus the severity of any accumulated delays.

WTT stands for working timetable. It is the rail industry's version of the public national timetable, and shows
all movements on the rail network, including freight trains, empty trains, and those coming in and out of depots.
It also includes unique identification codes for each train, and intermediate times for journeys,
including which stations a train is not scheduled to stop at ([NR](https://www.networkrail.co.uk/running-the-railway/the-timetable/working-timetable/)).

##### Script contacts

Ask Tom Winterbottom, Hudson, Greg, or Adam (adam.leach@durham.ac.uk).

## Weather

### MIDAS stations

Station data can be downloaded as a KMZ file from CEDA [here](http://artefacts.ceda.ac.uk/midas/midas_stations_by_area.kmz).
To avoid having to parse such a file, a list of stations can be downloaded by constructing an appropriate
query string (for which a function is provided) for the "Display station details" input at the CEDA site [here](http://archive.ceda.ac.uk/midas_stations/).
The output of this query is "excel_list_stations_details.csv".

There are 507 stations, but several are located overseas. The list can be reduced by filtering out:
* those that have closed (`Station end date == "Current "`)
* those on islands (`Area type == "ISLAND "`)
* those overseas (`Area type == "COUNTRY "`)
* those in remote Scottish regions (`Area type == "SCOTTISH_REGION "`)

451 remain. They are geolocated by `latitude`, `longitude`, `postcode`, and `area`. Every MIDAS observation contains the 
`src_id` of the station that recorded it - conveniently, the index of the output dataframe. 

### Historic weather data

Data comes from the Met Office via MIDAS (Met Office Integrated Data Archive System).
The primary dataset covers the 2018 - 2019 financial year; the output is therefore restricted to this data period.

The data is downloaded via FTP from the Centre for Environmental Analysis (CEDA) servers. Each year is about 1 GB.
The headers of the resulting CSV files can be found [here](https://artefacts.ceda.ac.uk/badc_datadocs/ukmo-midas/WH_Table.html).

In order for the model to be able to use weather *forecast* data, it must be trained on weather forecast data. 
So the historic weather data must be converted. After correspondence with CEDA to clarify some fields:

`wind_speed_unit_id` determines the wind speed unit:
* 0: wind speed estimated (m/s)
* 1: wind speed from anemometer (m/s)
* 3: wind speed estimated (knots)
* 4: wind speed from anemometer (knots)

Forecast wind speeds are in mph, so both were converted.

`src_opr_type` determines the type of observation:
1. Manual operation with significant weather reported (codes 04 - 99)
2. Manual operation with no significant weather reported.
3. Manual observation with weather included but not observed throughout the whole period. Usually reported at 0600, when
observations have been automatic overnight and the observer has come on duty at 0530
4. Automatic observation weather omitted (due to malfunction)
5. Automatic observation at site with weather sensor installed but not significant weather reported
6. Automatic observation with no weather sensor installed.
7. Automatic observation from site with weather sensor installed and weather reported. 

Manual and automatic observations have different weather codes (i.e. `prst_wx_id`) and so a manual mapping from
both manual and automatic codes (found [here](https://artefacts.ceda.ac.uk/badc_datadocs/surface/code.html#presweath))
to the forecast weather types ([here](https://www.metoffice.gov.uk/services/data/datapoint/code-definitions)) was 
painstakingly constructed. The forecast data format limited the usable fields to:
* Wind Gust (mph)
* Relative Humidity
* Temperature (C)
* Visibility
* Wind direction (compass)
* Wind speed (mph)
* Weather type
* Precipitation probability (%)

### Forecasts

The service used is Met Office Datapoint. Regional forecasts can be obtained up to 5 days in advance, and national to up
to 30 days. There are approximately 5000 UK forecast sites. A map must be created between MIDAS stations and 
Datapoint forecast sites for future model use. An API reference for Datapoint can be found 
[here](https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/data/datapoint_api_reference.pdf).
This will be explored in more depth at a much later date; for now, provision has been made to do so.

There are (officially) 30 weather types, defined [here](https://www.metoffice.gov.uk/services/data/datapoint/code-definitions).
In practice, there are 21 distinct types, as several have day and night variants, or are unused:

| Value | Description               | Maps to...        |
|-------|---------------------------|-------------------|
| NA    | Not available             | Not available     |
| 0     | Clear night               | Clear             |
| 1     | Sunny day                 | Clear             |
| 2     | Partly cloudy (night)     | Partly cloudy     |
| 3     | Partly cloudy (day)       |                   |
| 4     | Not used                  | N/A               |
| 5     | Mist                      | Mist              |
| 6     | Fog                       | Fog               |
| 7     | Cloudy                    | Cloudy            |
| 8     | Overcast                  | Overcast          |
| 9     | Light rain shower (night) | Light rain shower |
| 10    | Light rain shower (day)   |                   |
| 11    | Drizzle                   | Drizzle           |
| 12    | Light rain                | Light rain        |
| 13    | Heavy rain shower (night) | Heavy rain shower |
| 14    | Heavy rain shower (day)   |                   |
| 15    | Heavy rain                | Heavy rain        |
| 16    | Sleet shower (night)      | Sleet shower      |
| 17    | Sleet shower (day)        |                   |
| 18    | Sleet                     | Sleet             |
| 19    | Hail shower (night)       | Hail shower       |
| 20    | Hail shower (day)         |                   |
| 21    | Hail                      | Hail              |
| 22    | Light snow shower (night) | Light snow shower |
| 23    | Light snow shower (day)   |                   |
| 24    | Light snow                | Light snow        |
| 25    | Heavy snow shower (night) | Heavy snow shower |
| 26    | Heavy snow shower (day)   |                   |
| 27    | Heavy snow                | Heavy snow        |
| 28    | Thunder shower (night)    | Thunder shower    |
| 29    | Thunder shower (day)      |                   |
| 30    | Thunder                   | Thunder           |

A code is also defined for visibility:

| Value | Description                    |
|-------|--------------------------------|
| UN    | Unknown                        |
| VP    | Very poor - less than 1 km     |
| PO    | Poor - between 1 - 4 km        |
| MO    | Moderate - between 4 - 10 km   |
| GO    | Good - between 10 - 20 km      |
| VG    | Very good - between 20 - 40 km |
| EX    | Excellent - more than 40 km    |