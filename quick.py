import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
         'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
         'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
         'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
         'bank_holiday_running', 'length', 'speed', 'delayed']

dtype = {key: "uint8" for key in dtype}

dtype.update({
    "status": "category",
    "category": "category",
    "power_type": "category",
    "timing_load": "category",
    "seating": "category",
    "sleepers": "category",
    "reservations": "category",
    "ATOC_code": "category",
    "destination_stanox_area": "category",
    "origin_stanox_area": "category",
    "destination": "category",
    "origin": "category"
})

df = pd.read_csv("data/dscm_w.csv", index_col=["uid"], parse_dates=["std", "sta", "atd", "ata"], dtype=dtype)

print(df.head())

print(df.info())

print(df.describe(include="datetime"))