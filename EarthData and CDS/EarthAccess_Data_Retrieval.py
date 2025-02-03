import pathlib
import os
import earthaccess
import datetime
import geopandas as gpd

main_dir = str(pathlib.Path(__file__).parent.resolve())

polygon = os.path.join(main_dir,'SIG_input','test2.geojson')
polygon = gpd.read_file(polygon)
extent  = polygon.total_bounds

output = os.path.join(main_dir,'EarthAccess_Output')

try:
    os.makedirs(output)
except:
    pass

# data to send to EA Request
ea_product = 'ASTGTM' #this value is for ASTER v003
# other codes can be searched here: https://lpdaac.usgs.gov/product_search
west = extent[0]
south= extent[1]
east = extent[2]
north= extent[3]
initial_time = "2000-01"
final_time   = "2020-12"

# accessing to EarthData, may change from user to user
auth = earthaccess.login()

results = earthaccess.search_data(
    short_name=ea_product,
    cloud_hosted=True,
    bounding_box=(west,south,east,north),
    # in some EA/ED products, temporal can be neglected
    #temporal=(initial_time,final_time),
    count=10)


today = datetime.date.today()
local_out = ea_product + " " + str(today)
local_out = os.path.join(output,local_out)
try:
    os.makedirs(local_out)
except:
    pass

earthaccess.download(results, local_out)
