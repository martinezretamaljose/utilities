import pathlib
import os
import cdsapi
import datetime
import geopandas as gpd

main_dir = str(pathlib.Path(__file__).parent.resolve())

polygon = os.path.join(main_dir,'SIG_input','test2.geojson')
polygon = gpd.read_file(polygon)
extent  = polygon.total_bounds

output = os.path.join(main_dir,'CDS_Output')

#create local output folder
try:
    os.makedirs(output)
except:
    pass

# ----- Some extra words: -----
# I'm using ERA5-Land because it has a much finer resolution (0.1 degrees)
# than ERA5 (0.25 degrees), but you can choose any CDS product you might need.
# Anyway, on the CDS platform/website there is a section where they show the
# API input.
# ----- About the download process: -----
# There is a limit of cells (horizontal x vertical x time) of 120000. If
# you try to download a whole year at once, you can only do it if your spatial
# extent is of 12 cells (horizontal x vertical) or less.
# In this case, I choose a monthly period, which allows me a spatial extent of
# 160 cells (horizontal x vertical)
# If your spatial extent is way too large, I heavily recommend you to
# download your files on daily timesteps, it will take longer, of course.

# data to send to CDS Request
dataset = "reanalysis-era5-land"
products = ["2m_temperature"] # check names on CDS platform
west = extent[0]
south= extent[1]
east = extent[2]
north= extent[3]
months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
days = ["01","02","03","04","05","06","07","08","09","10",
        "11","12","13","14","15","16","17","18","19","20",
        "21","22","23","24","25","26","27","28","29","30","31"]
hours = ["00:00","01:00","02:00","03:00","04:00","05:00",
         "06:00","07:00","08:00","09:00","10:00","11:00",
         "12:00","13:00","14:00","15:00","16:00","17:00",
         "18:00","19:00","20:00","21:00","22:00","23:00"]
initial_year = 2023
final_year   = 2023

# connect to CDS API
cds = cdsapi.Client()

# create local output folder, so data will not get mixed
today = datetime.date.today()
local_out = dataset + " " + str(today)
local_out = os.path.join(output,local_out)
try:
    os.makedirs(local_out)
except:
    pass

for i in range(initial_year,final_year+1):
    for j in range(len(months)):
        output_file_name = str(i)+"-"+months[j] + ".nc"
        print(output_file_name)
        request= {
            "variable" : products,
            "year" : str(i),
            "month" : months[j],
            "day" : days,
            "time": hours,
            "data_format" : "netcdf",
            "download_format" : "unarchived",
            "area" : [north,west,south,east]}
        target = os.path.join(local_out , output_file_name)
        cds.retrieve(dataset, request, target)

