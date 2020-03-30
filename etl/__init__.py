from etl.extract import extract
from etl.transform import transform
from etl.load import load

start = "2018-04-01"
end = "2019-04-01"

extract(start, end)
transform()
load()
