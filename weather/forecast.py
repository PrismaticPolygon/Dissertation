import requests
import datapoint

conn = datapoint.connection(api_key="c9069456-63b7-40ea-97ae-13ff8f2f05de")

site = conn.get_nearest_forecast_site(51.500728, -0.124626)

print(site)

forecast = conn.get_forecast_for_site(site.id)

# A list of timesteps

print(forecast)

print(forecast.now().weather.text)



# API reference: https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/data/datapoint_api_reference.pdf

# url = "http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/regionalforecast/xml/sitelist"
# url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist"
# # https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/data/datapoint_api_reference.pdf#page=18&zoom=100,0,525
#
# r = requests.get(url, {"key": "c9069456-63b7-40ea-97ae-13ff8f2f05de"})
#
# locations = r.json()["Locations"]["Location"]
#
# auth_areas = []
#
# print(locations[0])

# Wow, this is dumb.

# forecast_url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3840"
#
# r = requests.get(forecast_url, {"key": "c9069456-63b7-40ea-97ae-13ff8f2f05de", "res": "3hourly"})
#
# site = r.json()["SiteRep"]
#
# # So the keys are Wx and DV. Wx contains static data, DV actual stuff.
#
# forecast = dict()
#
# for param in site["Wx"]["Param"]:
#
#     forecast[param["name"]] = {"units": param["units"], "description": param["$"]}
#
# forecast["date"] = site["DV"]["dataDate"]
# forecast["id"] = site["DV"]["Location"]["i"]
# forecast["latitude"] = site["DV"]["Location"]["lat"]
# forecast["longitude"] = site["DV"]["Location"]["lon"]
# forecast["name"] = site["DV"]["Location"]["name"]
#
# print(forecast)

# Oh, I see. It's to avoid.. right.
# So my API should... iy doens't really matter. All that does are the fields.

# Wind Gust (mph)
# Relative Humidity
# Temperature (C)
# Visibility
# Wind direction (compass)
# Wind speed (mph)
# Weather type
# Precipitation probability (%)

# I think that precipitation probability is too important to ignore.

# Weather types: https://www.metoffice.gov.uk/services/data/datapoint/code-definitions

# So again: we want to make this into a record, I guess.
#
# for p in site["DV"]["Location"]["Period"]:
#
#     print(p)

    # print(site["DV"][key])





# print(params)

# for key in site:
#
#     print(key)
#
#     print(site[key])

# for location in locations:
#
#     # if "unitaryAuthArea" in location and location["unitaryAuthArea"] not in auth_areas:
#     #
#     #     auth_areas.append(location["unitaryAuthArea"])
#
# # Okay! Tha's more like it.
# # So these are the... regions? That I can get stuff for.
# # right?
#
# for area in sorted(auth_areas):
#
#     print(area)

#
# locations = r.json()["Locations"]["Location"]
#
# locations = [{"id": location["@id"], "name": location["@name"]} for location in locations]
#
# for location in locations:
#
#     print(location)

#
#
# meta = {'F': {'units': 'C', 'description': 'Feels Like Temperature'}, 'G': {'units': 'mph', 'description': 'Wind Gust'}, 'H': {'units': '%', 'description': 'Screen Relative Humidity'}, 'T': {'units': 'C', 'description': 'Temperature'}, 'V': {'units': '', 'description': 'Visibility'}, 'D': {'units': 'compass', 'description': 'Wind Direction'}, 'S': {'units': 'mph', 'description': 'Wind Speed'}, 'U': {'units': '', 'description': 'Max UV Index'}, 'W': {'units': '', 'description': 'Weather Type'}, 'Pp': {'units': '%', 'description': 'Precipitation Probability'}, 'date': '2019-11-12T23:00:00Z', 'id': '3840', 'latitude': '50.86', 'longitude': '-3.239', 'name': 'DUNKESWELL AERODROME'}
# forecast = {'type': 'Day', 'value': '2019-11-16Z', 'Rep': [{'D': 'NNW', 'F': '-1', 'G': '22', 'H': '91', 'Pp': '2', 'S': '11', 'T': '4', 'V': 'VG', 'W': '2', 'U': '0', '$': '0'}, {'D': 'NNW', 'F': '-1', 'G': '22', 'H': '91', 'Pp': '30', 'S': '11', 'T': '4', 'V': 'GO', 'W': '9', 'U': '0', '$': '180'}, {'D': 'NNW', 'F': '-1', 'G': '20', 'H': '93', 'Pp': '11', 'S': '11', 'T': '3', 'V': 'VG', 'W': '2', 'U': '0', '$': '360'}, {'D': 'NNW', 'F': '0', 'G': '20', 'H': '91', 'Pp': '7', 'S': '11', 'T': '5', 'V': 'GO', 'W': '7', 'U': '1', '$': '540'}, {'D': 'NNW', 'F': '2', 'G': '20', 'H': '86', 'Pp': '9', 'S': '11', 'T': '6', 'V': 'MO', 'W': '7', 'U': '1', '$': '720'}, {'D': 'NNW', 'F': '4', 'G': '16', 'H': '84', 'Pp': '10', 'S': '9', 'T': '7', 'V': 'VG', 'W': '8', 'U': '1', '$': '900'}, {'D': 'NW', 'F': '3', 'G': '11', 'H': '89', 'Pp': '7', 'S': '7', 'T': '5', 'V': 'VG', 'W': '7', 'U': '0', '$': '1080'}, {'D': 'WSW', 'F': '2', 'G': '9', 'H': '92', 'Pp': '6', 'S': '7', 'T': '5', 'V': 'VG', 'W': '7', 'U': '0', '$': '1260'}]}
# # Okay. I don't care about feels - like temperature.
# # If I get it like this....
# # How do I convert?
#
# # Then we're given...
# # A lot of shite, basically.
# # From that... I'm trying to make a dictionary using my existing keys.
#
# map = {
#     "G": "wind_gust",
#     "H": "relative_humidity",
#     "T": "temperature",
#     "D": "wind_direction",
#     "S": "wind_speed",
#     "W": "weather_type",
# }
#
# record = dict()
#
# print(len(forecast["Rep"]))
#
# # 8, because it's three-hourly.
#
# for key in forecast:
#
#     pass
#     # record["ob_time"] =
#
#
# #
# # for key in meta:
# #
# #     print(key, meta[key])
#
#






























