# Dates

The 2018 - 2019 UK financial year runs from 1/4/2018 to 3/31/2019.
This period was chosen for two main reasons:

1. It is the period covered by ORR's station usage statistics.
2. It is the period covered by NR's historic delay attribution data.

It imposes only a slight overhead on the weather data-set, which is released in calendar years. The primary data-set is
released in days and so is unaffected

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