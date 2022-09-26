rm(list = ls())

library("lubridate")

### Read forecast
fc = read.csv("final_forecast.csv")

### timestamp vectors
t = c()
cur_time = "01-10-2020 00:00:00" 
cur_time = as.POSIXct(cur_time, "%d-%m-%Y %H:%M:%OS", tz = "UTC")


for (i in 1:length(fc[,1])){
  t = append(t, cur_time)
  cur_time = cur_time + minutes(15)
}

fc$timestamp = t

### Convert to long
library(tidyr)
fc <- gather(fc, building, energyDemand, Building0:Building6, factor_key=TRUE)
fc <- gather(fc, solar, powerProduction, Solar0:Solar5, factor_key=TRUE)


### Get building 0-3
b03 = c()
for (i in 1:length(fc[,1])){
  if (fc$building[i] == "Building0"){
    b03 = append(b03, i)
  }
  else if (fc$building[i] == "Building1"){
    b03 = append(b03, i)
  }
  else if (fc$building[i] == "Building3"){
    b03 = append(b03, i)
  }
}

building03 = fc[b03,]
building03 = building03[,c("timestamp","building","energyDemand")]

write.csv(building03, "final_forecast_building03.csv", row.names = FALSE)


### Get building 4-6
b46 = c()
for (i in 1:length(fc[,1])){
  if (fc$building[i] == "Building4"){
    b46 = append(b46, i)
  }
  else if (fc$building[i] == "Building5"){
    b46 = append(b46, i)
  }
  else if (fc$building[i] == "Building6"){
    b46 = append(b46, i)
  }
}

building46 = fc[b46,]
building46 = building46[,c("timestamp","building","energyDemand")]

write.csv(building46, "final_forecast_building46.csv", row.names = FALSE)


### Get solar 0-2
s02 = c()
for (i in 1:length(fc[,1])){
  if (fc$solar[i] == "Solar0"){
    s02 = append(s02, i)
  }
  else if (fc$solar[i] == "Solar1"){
    s02 = append(s02, i)
  }
  else if (fc$solar[i] == "Solar2"){
    s02 = append(s02, i)
  }
}

Solar02 = fc[s02,]
Solar02 = Solar02[,c("timestamp","solar","powerProduction")]

write.csv(Solar02, "final_forecast_solar02.csv", row.names = FALSE)


### Get solar 3-5
s35 = c()
for (i in 1:length(fc[,1])){
  if (fc$solar[i] == "Solar3"){
    s35 = append(s35, i)
  }
  else if (fc$solar[i] == "Solar4"){
    s35 = append(s35, i)
  }
  else if (fc$solar[i] == "Solar5"){
    s35 = append(s35, i)
  }
}

Solar35 = fc[s35,]
Solar35 = Solar35[,c("timestamp","solar","powerProduction")]

write.csv(Solar35, "final_forecast_solar35.csv", row.names = FALSE)


### write to csv
write.csv(fc, "final_forecast_timestamp_long.csv", row.names = FALSE)









