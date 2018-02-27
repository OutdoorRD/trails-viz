library(dplyr)
library(foreign)
library(raster)
library(tidyr)
library(lubridate)

setwd('~/mbsnf/trails-viz/')

mon_pr <- read.csv('scratch/viz_model_mbs_trails_v5_mmm_20180227.csv')
mon_ir <- read.csv('scratch/viz_model_mbs_trails_v5_mmmir_20180227.csv')

idvars <- c("trail", "d2p", "month")

prediction <- "jjlmexp"
mon_pr <- mon_pr[ ,c(idvars, prediction)]

response <- "ir.ss"
mon_ir <- mon_ir[ ,c(idvars, response)]

monthly <- left_join(mon_pr, mon_ir, by=idvars)
names(monthly) <- c("AllTRLs_ID", "date", "month", "predicted", "actual")

## subset sarah's trails
trails <- read.dbf("scratch/SARL_AllTrls.dbf")
out <- monthly[which(monthly$AllTRLs_ID %in% trails$ALLTRLs_ID),]

## join trail name
link <- read.dbf("/home/dmf/mbsnf/mbs-trails/gis/AllTRLs_v4.dbf")
out2 <- left_join(out, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")

write.csv(out2, 'static/data/hikers_monthly.csv', row.names = F)


## monthly avg for lines
avgmon <- out2 %>%
  group_by(AllTRLs_ID, month) %>%
  summarize(avg_pred=mean(predicted, na.rm=T))

avgmon$month <- month.abb[avgmon$month]

avgmon_wide <- spread(avgmon, month, c(avg_pred))

## add data to lines
lines <- shapefile("scratch/SARL_AllTrls.shp")
dat <- lines@data
names(dat) <- "AllTRLs_ID"
dat$AllTRLs_ID <- as.numeric(dat$AllTRLs_ID)

## join trail name
dat2 <- left_join(dat, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")
dat3 <- left_join(dat2, avgmon_wide, by="AllTRLs_ID")



# library(ggplot2)
# library(lubridate)
# monthly$date <- ymd(monthly$d2p)
# 
# ggplot(out2, aes(x=date)) +
#   geom_line(aes(y=jjlmexp), color='blue') +
#   geom_line(aes(y=ir.ss), color='orange') +
#   facet_wrap("Trail_name")