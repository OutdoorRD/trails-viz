library(dplyr)
library(foreign)
library(raster)
library(tidyr)
library(lubridate)
library(rgdal)

setwd('~/mbsnf/trails-viz/')

# idvars <- c("trail", "d2p", "month")
idvars <- c("trail", "d2p")
prediction <- "jjmm"
response <- "resp.ss"

## load monthly
mon_pr <- read.csv('scratch/viz_model_mbs_trails_v6_mmm_20180227.csv')
mon_ir <- read.csv('scratch/viz_model_mbs_trails_v6_mmmir_20180227.csv')

mon_pr <- mon_pr[ ,c(idvars, prediction)]
mon_ir <- mon_ir[ ,c(idvars, response)]

monthly <- left_join(mon_pr, mon_ir, by=idvars)
names(monthly) <- c("AllTRLs_ID", "date", "predicted", "actual")
# names(monthly) <- c("AllTRLs_ID", "date", "month", "predicted", "actual")

## load weekly
week_pr <- read.csv('scratch/viz_model_mbs_trails_v6_www_20180227.csv')
week_ir <- read.csv('scratch/viz_model_mbs_trails_v6_wwwir_20180227.csv')

week_pr <- week_pr[ ,c(idvars, prediction)]
week_ir <- week_ir[ ,c(idvars, response)]

weekly <- left_join(week_pr, week_ir, by=idvars)
names(weekly) <- c("AllTRLs_ID", "date", "predicted", "actual")

## subset sarah's trails
trails <- read.dbf("scratch/SARL_AllTrls.dbf")
out_mon <- monthly[which(monthly$AllTRLs_ID %in% trails$ALLTRLs_ID),]
out_week <- weekly[which(weekly$AllTRLs_ID %in% trails$ALLTRLs_ID),]

## join trail name
link <- read.dbf("/home/dmf/mbsnf/mbs-trails/gis/AllTRLs_v4.dbf")
out_mon2 <- left_join(out_mon, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")
out_week2 <- left_join(out_week, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")

### DIVIDE by 2 - since we never did that for IR counts
### MOVE THIS UPSTREAM, BEFORE MODELING
## also limit precision in predicted vals
out_mon2$predicted <- round(out_mon2$predicted/2, 2)
out_mon2$actual <- out_mon2$actual/2
out_week2$predicted <- round(out_week2$predicted/2, 2)
out_week2$actual <- out_week2$actual/2

write.csv(out_mon2, 'static/data/hikers_monthly.csv', row.names = F)
write.csv(out_week2, 'static/data/hikers_weekly.csv', row.names = F)


# ## monthly avg for lines
# avgmon <- out2 %>%
#   group_by(AllTRLs_ID, month) %>%
#   summarize(avg_pred=mean(predicted, na.rm=T))
# 
# avgmon$month <- month.abb[avgmon$month]
# 
# avgmon_wide <- spread(avgmon, month, c(avg_pred))

## add data to lines
lines <- shapefile("scratch/SARL_AllTrls.shp")
dat <- lines@data
names(dat) <- "AllTRLs_ID"
dat$AllTRLs_ID <- as.numeric(dat$AllTRLs_ID)

## join trail name
dat2 <- left_join(dat, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")
# dat3 <- left_join(dat2, avgmon_wide, by="AllTRLs_ID")
lines@data <- dat2

writeOGR(lines, "static/data/trails", layer="trails", driver="GeoJSON", overwrite_layer = T)

# library(ggplot2)
# library(lubridate)
# monthly$date <- ymd(monthly$d2p)
# 
# ggplot(out2, aes(x=date)) +
#   geom_line(aes(y=jjlmexp), color='blue') +
#   geom_line(aes(y=ir.ss), color='orange') +
#   facet_wrap("Trail_name")