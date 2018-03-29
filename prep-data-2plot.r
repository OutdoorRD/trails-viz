library(dplyr)
library(foreign)
library(raster)
library(tidyr)
library(lubridate)
library(rgdal)

# idvars <- c("trail", "d2p", "month")
idvars <- c("trail", "d2p")
prediction <- "jjmm"
response <- "resp.ss"

out_fieldnames <- c("AllTRLs_ID", "date", "predicted", "actual")

## load monthly
mon_pr <- read.csv('scratch/viz_model_mbs_trails_v7_mmm_20180315.csv')
mon_ir <- read.csv('scratch/viz_model_mbs_trails_v7_mmmir_20180315.csv')

mon_pr <- mon_pr[, c(idvars, prediction)]
mon_ir <- mon_ir[, c(idvars, response)]
monthly <- left_join(mon_pr, mon_ir, by=idvars)

monthly <- separate(data=monthly, col=d2p, into=c("year", "month", "day"), sep="-", remove=T)
monthly$date <- paste(monthly$year, monthly$month, sep="-")
monthly <- monthly[,c("trail", "date", prediction, response, "year", "month")]

names(monthly) <- c(out_fieldnames, "year", "month")

## load weekly
week_pr <- read.csv('scratch/viz_model_mbs_trails_v6_www_20180227.csv')
week_ir <- read.csv('scratch/viz_model_mbs_trails_v6_wwwir_20180227.csv')

week_pr <- week_pr[ ,c(idvars, prediction)]
week_ir <- week_ir[ ,c(idvars, response)]

weekly <- left_join(week_pr, week_ir, by=idvars)
names(weekly) <- out_fieldnames

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

write.csv(out_mon2[, c(out_fieldnames, "Trail_name")], 'static/data/hikers_monthly.csv', row.names = F)
write.csv(out_week2, 'static/data/hikers_weekly.csv', row.names = F)


## monthly avg for histograms
avgmon <- out_mon2 %>%
  group_by(AllTRLs_ID, month) %>%
  summarize(avg_pred=round(mean(predicted, na.rm=T), digits=0))

for(id in unique(avgmon$AllTRLs_ID)){
  monout <- avgmon[avgmon$AllTRLs_ID == id,]
  write.csv(monout, file=file.path("static/data/monthlies", paste0(id, ".csv")), row.names=F)
}

# avgmon$month <- month.abb[avgmon$month]
# avgmon_wide <- spread(avgmon, month, c(avg_pred))

## annual avg for histograms
avgann <- out_mon2 %>%
  group_by(AllTRLs_ID, year) %>%
  summarize(avg_pred=round(mean(predicted, na.rm=T), digits=0))

for(id in unique(avgann$AllTRLs_ID)){
  annout <- avgann[avgann$AllTRLs_ID == id,]
  write.csv(annout, file=file.path("static/data/annuals", paste0(id, ".csv")), row.names=F)
}

## annual total for line weight
annual <- out_mon2 %>%
  filter(year == "2017") %>%
  group_by(AllTRLs_ID) %>%
  summarize(annual=sum(predicted, na.rm=T))
annual$annual <- log(annual$annual)

## load lines
lines <- shapefile("scratch/SARL_AllTrls.shp")
lines <- spTransform(lines, CRS("+proj=longlat +datum=WGS84 +no_defs"))
dat <- lines@data
names(dat) <- "AllTRLs_ID"
dat$AllTRLs_ID <- as.numeric(dat$AllTRLs_ID)

# join data to lines
dat2 <- left_join(dat, link[,c("AllTRLs_ID", "Trail_name")], by="AllTRLs_ID")
dat3 <- left_join(dat2, annual, by="AllTRLs_ID")
lines@data <- dat3
#
# THIS DOES NOT WORK - don't use rgdal for this.
# writeOGR(lines, dsn="static/data/trails.geojson", layer="layer", driver="GeoJSON")
# this works, wtf
writeOGR(lines, dsn="static/data/trails", layer="layer", driver="GeoJSON")
system("mv static/data/trails static/data/trails.geojson")

# library(ggplot2)
# library(lubridate)
# monthly$date <- ymd(monthly$d2p)
# 
# ggplot(out2, aes(x=date)) +
#   geom_line(aes(y=jjlmexp), color='blue') +
#   geom_line(aes(y=ir.ss), color='orange') +
#   facet_wrap("Trail_name")