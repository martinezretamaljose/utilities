library(rstudioapi)
library(stringr)
library(terra)
library(ncdf4)
library(readxl)
library(writexl)
library(zoo)
library(lubridate)

# 1: Clear console
rm(list=ls()); gc(); graphics.off()

# 2: Setting current file's directory as main directory
main <- dirname(getActiveDocumentContext()$path)

# 3: Calling basin polygon
#    - This polygon is in WGS84 UTM 19S (EPSG:32719), while netcdf files are in 
#      WGS84 (EPSG:4326). Polygon must be reprojected into 4326 before using
basin <- vect(file.path(main,'sig_input','bandas_elevacion.geojson'))
basin <- project(basin,'epsg:4326')
plot(basin,axes=T) # Check if it was properly re-projected.

# 4: Calling ncdf files
#    - CR2MET v2.5 files are composed of two main groups: precipitation files 
#      and temperature (min and max in a combined .nc) files, separated by 
#      months. 
#    - It is very important that both files must start and end at the same 
#      time stamps (e.g. 2014-06 to 2014-08)

pr_files <- intersect(list.files(file.path(main,'ncdf'),pattern='_pr_'),
                      list.files(file.path(main,'ncdf'),pattern='.nc*'))

ta_files <-  intersect(list.files(file.path(main,'ncdf'),pattern='_tmin_tmax_'),
                       list.files(file.path(main,'ncdf'),pattern='.nc*'))

# 5: Defining time length of data series - Which is based in how much files do
#    we have
time_blocks <- substr(pr_files,20,26)
min_tb <- time_blocks[1]
max_tb <- time_blocks[length(time_blocks)]

start_date <- as.Date(paste(as.numeric(substr(min_tb,1,4)),
                            as.numeric(substr(min_tb,6,7)),
                            '01',sep='-'))
end_date <- as.Date(paste(as.numeric(substr(max_tb,1,4)),
                          as.numeric(substr(max_tb,6,7)),
                          days_in_month(as.numeric(substr(max_tb,6,7))),
                          sep='-'))

date_series <- seq(start_date,end_date,1)

# 6: creating base dataframe for time series
nsub <- length(basin)
# on this example, years, months and days are allocated in different columns.
df <- as.data.frame(matrix(0,ncol=3+nsub,nrow=length(date_series)))
colnames(df) <- c('year','month','day',basin$DN)
df$year <- as.numeric(substr(date_series,1,4))
df$month <- as.numeric(substr(date_series,6,7))
df$day <- as.numeric(substr(date_series,9,10))

# console clearing: non essential parameters
rm(date_series,end_date,max_tb,min_tb,time_blocks)

# 7: Create extension for data retrieval
bbox <- ext(basin)@pntr[["vector"]]
xmin <- bbox[1] - 0.025
xmax <- bbox[2] + 0.025
ymin <- bbox[3] - 0.025
ymax <- bbox[4] + 0.025

nct <- nc_open(file.path(main,'ncdf',pr_files[1]))
lon <- as.data.frame(nct$dim$lon$vals)
lat <- as.data.frame(nct$dim$lat$vals)
ac_lon <- lon[which(lon >= xmin & lon <= xmax),]
ac_lat <- lat[which(lat >= ymin & lat <= ymax),]

lserv <- length(ac_lon)*length(ac_lat)

img_df <- as.data.frame(matrix(0,
                               ncol=3,
                               nrow=lserv
))
colnames(img_df) <- c('Lon','Lat','Z')
i=1
for (i in 1:length(ac_lon)){
  j=1
  for (j in 1:length(ac_lat)){
    k= j + (i-1)*length(ac_lat)
    img_df$Lon[k] <- ac_lon[i]
    img_df$Lat[k] <- ac_lat[j]
    img_df$Z[k] <- k
    
  }
}
# From XYZ to Raster
img <- rast(img_df,type='xyz')
plot(img)
# From Raster to Polygon
img_pol <- as.polygons(img)
plot(img_pol)
crs(img_pol) <- 'EPSG:4326'

# create dataframes for each parameter
pr_df <- tmin_df <- tmax_df <- t2m_df <- df

# 8: Filling data series

w = 1
for(w in 1:nsub){
  sub_basin <- basin[w,]
  sub_grid <- crop(img_pol,sub_basin)
  grid <- as.data.frame(sub_grid)
  grid$pond <- expanse(sub_grid)/sum(expanse(sub_grid))
  z=1
  for(z in 1:length(pr_files)){
    pr_nc <- nc_open(file.path(main,'ncdf',pr_files[z]))
    ta_nc <- nc_open(file.path(main,'ncdf',ta_files[z]))
    z_year <- as.numeric(substr(pr_files[z],20,23)) 
    z_month <- as.numeric(substr(pr_files[z],25,26))
    print(paste0(z_year,' / ',z_month),quote=F)
    time_loc <- which(df$year == z_year & df$month==z_month)
    x_pr <- x_tmin <- x_tmax <- x_tavg <- matrix(0,ncol=1,nrow=length(time_loc))
    t=1
    for(t in 1:nrow(grid)){
      grid_cell <- grid$Z[t]
      grid_pond <- grid$pond[t]
      grid_lon <- img_df$Lon[grid_cell]
      grid_lat <- img_df$Lat[grid_cell]
      i=which(lon==grid_lon)
      j=which(lat==grid_lat)
      
      y_pr <- ncvar_get(pr_nc, varid = 'pr', start=c(i,j,1),count=c(1,1,-1))
      y_tmin <- ncvar_get(ta_nc, varid = 'tmin', start=c(i,j,1),count=c(1,1,-1))
      y_tmax <- ncvar_get(ta_nc, varid = 'tmax', start=c(i,j,1),count=c(1,1,-1))
      y_tavg <- 0.5*(y_tmin + y_tmax)
      
      x_pr <- x_pr + as.matrix(grid_pond*y_pr)
      x_tmin <- x_tmin + as.matrix(grid_pond*y_tmin)
      x_tmax <- x_tmax + as.matrix(grid_pond*y_tmax)
      x_tavg <- x_tavg + as.matrix(grid_pond*y_tavg)
    }
    pr_df[time_loc,w+3] <- round(x_pr,3)
    tmin_df[time_loc,w+3] <- round(x_tmin,2)
    tmax_df[time_loc,w+3] <- round(x_tmax,2)
    t2m_df[time_loc,w+3] <- round(x_tavg,2)
    
  }
}

# 9: save files
write.table(pr_df,file.path(main,'pr_data.csv'),
            col.names = T, row.names = F, sep=',')
write.table(tmin_df,file.path(main,'tmin_data.csv'),
            col.names = T, row.names = F, sep=',')
write.table(tmax_df,file.path(main,'tmax_data.csv'),
            col.names = T, row.names = F, sep=',')
write.table(t2m_df,file.path(main,'t2m_data.csv'),
            col.names = T, row.names = F, sep=',')
