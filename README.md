# Dissertation

This repository contains my dissertation. The aim is to predict medium-term train delays. *Medium-term* refers to trains
which have not left yet their origin. A *delay* is a positive variation (of greater than 5 minutes) between the
scheduled arrival of a train at its destination and the actual time of arrival.

## Dataset

The outcome of my project is twofold: a dataset, and a model. The dataset is of shape `(5205458, 47)` and is available 
for download as `data/dscm.csv`. 

#### License

All data used to construct the dataset is freely available under [version 2 of the Open Government
License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/), which gives the right to:
* "copy, publish, distribute and transmit the Information"
* "adapt the Information"
* "exploit the Information commercially and non-commercially for example, by combining it with other Information, or by 
including it in your own product or application"

By referencing it here I fulfill my obligation to "acknowledge the source of the Information by including any attribution statement specified by the Information Provider(s) and, where possible, provide a link to this licence".

### Config

To download data, five constants must be stored in `config.py`:

| Field                  | Description                                                                                                                    |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| CEDA_USERNAME          | A username for accessing CEDA. See [here](https://services.ceda.ac.uk/cedasite/register/info/).                                |                                                                           |
| CEDA_PASSWORD          | A password for accessing CEDA.                                                                                                 |
| NR_USERNAME            | A username for accessing NR data feeds. See [here](https://opendata.nationalrail.co.uk/registration).                          |
| NR_PASSWORD            | A password for accessing NR.                                                                                                   |
| NR_EMAIL               | An email for accessing NR.                                                                                                     |

## Location

`data/location.csv` contains geolocated TIPLOCs. 

| field       | description                                                           |
|-------------|-----------------------------------------------------------------------|
| atco        |                                                                       |
| tiploc      | The TIPLOC (timing point location) of this location                   |
| 3alpha      |                                                                       |
| nlcdesc     |                                                                       |
| nlc         |                                                                       |
| stanox      | The STANOX of this location                                           |
| stanox_area | The STANOX area of this location                                      |
| latitude    | The latitude of the location                                          |
| longitude   | The longitude of the location                                         |
| src_id      | The MIDAS station src_id this location is closest to                  |
| distance    | The distance (km) between this location and the closest MIDAS station |

## Weather

### MIDAS stations

Station data can be downloaded as a [KMZ file from CEDA](http://artefacts.ceda.ac.uk/midas/midas_stations_by_area.kmz).

There are 507 stations. Those that are inactive, or located overseas, are filtered out. 451 remain. 
They are geolocated by `latitude`, `longitude`, `postcode`, and `area`. Every MIDAS observation contains the 
`src_id` of the station that recorded it; this is used to join the datasets together. 

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