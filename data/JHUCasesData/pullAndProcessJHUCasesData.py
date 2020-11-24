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

class JHUCasesData(object):
    def __init__(self):
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
        self.casesdata_w = pd.read_csv(url)
        self.fromWide2Long()

        self.UStotal()
        
    def fromWide2Long(self):
        import re
        vvs = [x for x in self.casesdata_w.columns if re.match("\d+[/]\d+[/]\d+",x)]
        casesdata_l = self.casesdata_w.melt( id_vars = ["FIPS"], value_vars = vvs )
        self.casesdata_l = casesdata_l.rename(columns={'variable':'date','value':'cases'})
        
    def UStotal(self):
        usTotalCases = self.casesdata_l.groupby(["date"]).sum().reset_index()[["date","cases"]]
        usTotalCases = EWandMW(usTotalCases).d

        # groupby EW
        def latest(x):
            x["date"] = [pd.to_datetime(_) for _ in x.date.values]
            x = x.sort_values("date")
            return x.iloc[-1]
        self.usTotalCases = usTotalCases.groupby(['EW']).apply(latest)
        
    def incidentCases(self):
        self.usTotalCases["inccases"] = self.usTotalCases.diff()["cases"]

def computeYticks(ys):
    ys = ys[~np.isnan(ys)]
    miny,maxy = min(ys),max(ys)
    return [int(y) for y in np.linspace( miny,maxy,10)]
        
if __name__ == "__main__":

    jhuDD = JHUCasesData()
    jhuDD.incidentCases()

    jhuNewCases = jhuDD.usTotalCases
    jhuNewCases = jhuNewCases.iloc[:-1,:]

    plt.style.use("fivethirtyeight")

    fig,ax = plt.subplots()
    ax.scatter( jhuNewCases.MW, jhuNewCases.inccases, s=10 )
    ax.plot( jhuNewCases.MW, jhuNewCases.inccases, lw=3, alpha=0.50)

    EWs = jhuNewCases.EW
    MWs = jhuNewCases.MW
    
    ax.set_xticks(MWs[::5])
    ax.set_xticklabels( [int(x) for x in EWs[::5]] )
 
    ax.tick_params(which="both",labelsize=8)

    ax.set_xlabel("Epiweek", fontsize=10)
    ax.set_ylabel("Num. of new cases due to COVID-19", fontsize=10)

    
    utc = datetime.utcnow().date()
    
    ax.text(0.01, 0.99, "Data as recent as {:d}-{:d}-{:d}".format( utc.year, utc.month, utc.day )
            ,weight="bold",fontsize=10,ha="left",va="top", color="#3d3d3d",transform=ax.transAxes)
    
    ax.set_yticks( computeYticks(jhuNewCases.inccases) ) 
    ax.set_yticklabels(["{:,}".format(y) for y in ax.get_yticks()])
                   
    fig.set_tight_layout(True)

    w = mm2inch(189)
    fig.set_size_inches(w,w/1.6)
    
    plt.savefig("numberOfNewCases.png")
    plt.close()
