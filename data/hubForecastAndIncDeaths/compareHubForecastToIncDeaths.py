#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import datetime

if __name__ == "__main__":

    incForecasts = pd.DataFrame()
    start = pd.to_datetime("2020-04-27")
    while True:
        dateString = "{:04d}-{:02d}-{:02d}".format(start.year,start.month,start.day)
        print(dateString)
        try:
            forecast = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/COVIDhub-ensemble/{:s}-COVIDhub-ensemble.csv".format(dateString) )
            _4wkincDeathForecast = forecast.loc[ (forecast.target=="4 wk ahead inc death") & (forecast.type=='quantile') & (forecast["quantile"]==0.50) & (forecast.location=="US"),: ]

            incForecasts = incForecasts.append(_4wkincDeathForecast)

            start = start + datetime.timedelta(days=7)
        except:
            break

    # grab the truth and compare
    incDeathsTruth = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Incident%20Deaths.csv")
    incDeathsTruth = incDeathsTruth.loc[incDeathsTruth.location=="US"]
    incDeathsTruth = incDeathsTruth.rename(columns = {"value":'truth'})
    incDeathsTruth["date"] = incDeathsTruth.date.astype("datetime64")
    
    weeklyIncDeaths = {"date":[], "weeklyTruth":[], 'sd':[], 'ed':[]}
    for (startDate,endDate) in zip(incForecasts.forecast_date, incForecasts.target_end_date):
        endDate = pd.to_datetime(endDate)
        startD  = endDate - datetime.timedelta(days=7)
        
        subset = incDeathsTruth.loc[ (incDeathsTruth.date >= startD) & (incDeathsTruth.date < endDate) ]
        sumDeaths = subset.truth.sum()

        weeklyIncDeaths["date"].append(endDate)
        weeklyIncDeaths["weeklyTruth"].append(sumDeaths)
        weeklyIncDeaths["sd"].append(startD)
        weeklyIncDeaths["ed"].append(endDate)
        
    weeklyIncDeaths = pd.DataFrame(weeklyIncDeaths)
    weeklyIncDeaths["date"] = weeklyIncDeaths.date.astype("str")
    
    forecastAndTruth = incForecasts.merge(weeklyIncDeaths, left_on = ["target_end_date"], right_on = ["date"])
    forecastAndTruth['factor'] = forecastAndTruth.weeklyTruth/forecastAndTruth.value

    todaysdate =  datetime.datetime.today()
    todayString = "{:04d}-{:02d}-{:02d}".format(todaysdate.year,todaysdate.month,todaysdate.day)
    
    forecastAndTruth = forecastAndTruth.loc[ forecastAndTruth.target_end_date < todayString,: ]

    print("Mean truth/median = {:.2f}".format(forecastAndTruth.factor.mean() ))
    print("SD truth/median = {:.2f}".format(forecastAndTruth.factor.std()))

    forecastAndTruth.to_csv("forecastHubMedianAndTruth.csv")
