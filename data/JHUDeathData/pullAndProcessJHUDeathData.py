#mcandrew

import sys

sys.path.append('../')
from helperFuncs.timeAndDates import EWandMW 
from helperFuncs.timeAndDates import buildDictionaryFromEW2EndDate

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime

def mm2inch(x):
    return x/25.4

class JHUDeathData(object):
    def __init__(self):
        url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
        self.deathdata_w = pd.read_csv(url)
        self.fromWide2Long()

        self.UStotal()
        
    def fromWide2Long(self):
        import re
        vvs = [x for x in self.deathdata_w.columns if re.match("\d+[/]\d+[/]\d+",x)]
        deathdata_l = self.deathdata_w.melt( id_vars = ["FIPS"], value_vars = vvs )
        self.deathdata_l = deathdata_l.rename(columns={'variable':'date','value':'deaths'})
        
    def UStotal(self):
        usTotalDeaths = self.deathdata_l.groupby(["date"]).sum().reset_index()[["date","deaths"]]
        usTotalDeaths = EWandMW(usTotalDeaths).d

        # groupby EW
        def latest(x):
            x["date"] = [pd.to_datetime(_) for _ in x.date.values]
            x = x.sort_values("date")
            return x.iloc[-1]
        self.usTotalDeaths = usTotalDeaths.groupby(['EW']).apply(latest)
        
    def incidentDeaths(self):
        self.usTotalDeaths["incdeaths"] = self.usTotalDeaths.diff()["deaths"]
        
    def outputRawData(self):
        self.deathdata_l.to_csv("./JHU_count_of_deaths.csv",index=False)

def computeYticks(ys):
    ys = ys[~np.isnan(ys)]
    miny,maxy = min(ys),max(ys)
    return [int(y) for y in np.linspace( miny,maxy,10)]
        
if __name__ == "__main__":

    jhuDD = JHUDeathData()
    jhuDD.incidentDeaths()

    # output raw data for forecasters
    jhuDD.outputRawData()

    jhuNewDeaths = jhuDD.usTotalDeaths
    jhuNewDeaths = jhuNewDeaths.iloc[:-1,:]

    past4weeks = jhuNewDeaths.incdeaths.iloc[-4:].values
    mn = np.mean(past4weeks)
    sd = np.std(past4weeks)
    
    print("Range of New Deaths for the past 4 weeks")
    print("Mean = {:.2f} and SD = {:.2f}".format(mn,sd) )
    print("Mn-sigma = {:.2f}, mean + 5 sigmaS = {:.2f}".format(mn-5*sd,mn+5*sd) )
 

    # output processed data for forecasters
    jhuNewDeaths.to_csv("jhuNewDeaths.csv")

    plt.style.use("fivethirtyeight")

    fig,ax = plt.subplots()
    ax.scatter( jhuNewDeaths.MW, jhuNewDeaths.incdeaths, s=10 )
    ax.plot( jhuNewDeaths.MW, jhuNewDeaths.incdeaths, lw=3, alpha=0.50)

    EWs = jhuNewDeaths.EW
    MWs = jhuNewDeaths.MW

    fromEW2Date = buildDictionaryFromEW2EndDate(EWs)
    
    ax.set_xticks(list(MWs[::5])+[MWs.iloc[-1]])
    ax.set_xticklabels( [ "{:s}".format(fromEW2Date[int(x)]) for x in list(EWs[::5]) + [EWs.iloc[-1]] ], rotation=45, ha="right" )
    
    ax.tick_params(which="both",labelsize=8)

    ax.set_xlabel("Week ending on this date", fontsize=10)
    ax.set_ylabel("Weekly sum of the num. of new deaths\n due to COVID-19", fontsize=10)
    
    utc = datetime.utcnow().date()
    
    ax.text(0.01, 0.99, "Data as recent as {:04d}-{:02d}-{:02d}".format( utc.year, utc.month, utc.day )
            ,weight="bold",fontsize=10,ha="left",va="top", color="#3d3d3d",transform=ax.transAxes)
    
    ax.set_yticks( computeYticks(jhuNewDeaths.incdeaths) ) 
    ax.set_yticklabels(["{:,}".format(y) for y in ax.get_yticks()])
                   
    fig.set_tight_layout(True)

    w = mm2inch(189)
    fig.set_size_inches(w,w/1.6)
    
    plt.savefig("numberOfNewDeaths.png")
    plt.close()

