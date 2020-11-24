#mcandrew

import sys

sys.path.append('../')
from helperFuncs.timeAndDates import EWandMW 

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

def computeYticks(ys):
    ys = ys[~np.isnan(ys)]
    miny,maxy = min(ys),max(ys)
    return [int(y) for y in np.linspace( miny,maxy,10)]
        
if __name__ == "__main__":

    jhuDD = JHUDeathData()
    jhuDD.incidentDeaths()

    jhuNewDeaths = jhuDD.usTotalDeaths
    jhuNewDeaths = jhuNewDeaths.iloc[:-1,:]

    plt.style.use("fivethirtyeight")

    fig,ax = plt.subplots()
    ax.scatter( jhuNewDeaths.MW, jhuNewDeaths.incdeaths, s=10 )
    ax.plot( jhuNewDeaths.MW, jhuNewDeaths.incdeaths, lw=3, alpha=0.50)

    EWs = jhuNewDeaths.EW
    MWs = jhuNewDeaths.MW
    
    ax.set_xticks(MWs[::5])
    ax.set_xticklabels( [int(x) for x in EWs[::5]] )
 
    ax.tick_params(which="both",labelsize=8)

    ax.set_xlabel("Epiweek", fontsize=10)
    ax.set_ylabel("Num. of new deaths due to COVID-19", fontsize=10)

    
    utc = datetime.utcnow().date()
    
    ax.text(0.01, 0.99, "Data as recent as {:d}-{:d}-{:d}".format( utc.year, utc.month, utc.day )
            ,weight="bold",fontsize=10,ha="left",va="top", color="#3d3d3d",transform=ax.transAxes)
    
    ax.set_yticks( computeYticks(jhuNewDeaths.incdeaths) ) 
    ax.set_yticklabels(["{:,}".format(y) for y in ax.get_yticks()])
                   
    fig.set_tight_layout(True)

    w = mm2inch(189)
    fig.set_size_inches(w,w/1.6)
    
    plt.savefig("numberOfNewDeaths.png")
    plt.close()

