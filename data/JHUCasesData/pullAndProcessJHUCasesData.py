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

    def outputRawData(self):
        self.casesdata_l.to_csv("./JHU_newcases_data.csv",index=False)

def computeYticks(ys):
    ys = ys[~np.isnan(ys)]
    miny,maxy = min(ys),max(ys)
    return [int(y) for y in np.linspace( miny,maxy,10)]
        
if __name__ == "__main__":

    jhuDD = JHUCasesData()
    jhuDD.incidentCases()

    jhuDD.outputRawData()
    
    jhuNewCases = jhuDD.usTotalCases
    jhuNewCases = jhuNewCases.iloc[:-1,:]

    plt.style.use("fivethirtyeight")

    fig,ax = plt.subplots()
    ax.scatter( jhuNewCases.MW, jhuNewCases.inccases, s=10 )
    ax.plot( jhuNewCases.MW, jhuNewCases.inccases, lw=3, alpha=0.50)

    print("Number of New Cases = {:.1f} on for most recent epiweek".format(jhuNewCases.inccases.iloc[-1]))
    
    EWs = jhuNewCases.EW
    MWs = jhuNewCases.MW

    fromEW2Date = buildDictionaryFromEW2EndDate(EWs)
    ax.set_xticks(list(MWs[::5])+[MWs.iloc[-1]])
    ax.set_xticklabels( [ "{:s}".format(fromEW2Date[int(x)]) for x in list(EWs[::5]) + [EWs.iloc[-1]] ], rotation=45, ha="right" )
    
    ax.tick_params(which="both",labelsize=8)

    ax.set_xlabel("Week ending on this date", fontsize=10)
    ax.set_ylabel("Weekly sum of the num. of new cases\n due to COVID-19", fontsize=10)

    
    utc = datetime.utcnow().date()
    
    ax.text(0.01, 0.99, "Data as recent as {:04d}-{:02d}-{:02d}".format( utc.year, utc.month, utc.day )
            ,weight="bold",fontsize=10,ha="left",va="top", color="#3d3d3d",transform=ax.transAxes)
    
    ax.set_yticks( computeYticks(jhuNewCases.inccases) ) 
    ax.set_yticklabels(["{:,}".format(y) for y in ax.get_yticks()])
                   
    fig.set_tight_layout(True)

    w = mm2inch(189)
    fig.set_size_inches(w,w/1.6)
    
    plt.savefig("numberOfNewCases.png",dpi=300)
    plt.close()
