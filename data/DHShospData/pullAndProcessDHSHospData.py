#mcandrew

import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

def mm2inch(x):
    return x/25.4

class dhsHosp(object):
    def __init__(self):
        import pandas as pd
        self.grabMetaData() # <- ping API and gran meta data for DHS dataset
        self.loadData()     # <- read data from the DHS website
        self.total()        # <- sum all columns across states for every date

    # - data pull
    def grabMetaData(self):
        import requests
        metadata = requests.get("https://healthdata.gov/api/3/action/package_show?id=83b4a668-9321-4d8c-bc4f-2bef66c49050&page=0")
        metaDataDict = metadata.json()
        if metaDataDict['success']:
            metaDataDict = metaDataDict['result'][0]
        self.metaDataDict = metaDataDict
            
    def loadData(self):
        import pandas as pd
        try:
            dataUrl =   self.metaDataDict['resources'][0]['url'] # <- this is the url used to download the latest data
            self.hospdata = pd.read_csv(dataUrl)
            self.hospdata = self.hospdata.fillna(0.)
        except:
            print("Error downloading data")
    
    # -  process
    def total(self):
        ushospdata = self.hospdata.groupby(['date']).sum().reset_index()
        self.rawdata = ushospdata

        # from daily to weekly
        from epiweeks import Week
        def addEpiWeek(x):
            EW = Week.fromdate(pd.to_datetime(x.date))
            x["EW"] = int("{:04d}{:02d}".format(EW.year,EW.week))
            return x
        ushospdata = ushospdata.apply(addEpiWeek ,1)
        ushospdata = ushospdata.groupby(["EW"]).sum().reset_index()
        def addMWWeek(x):
            from epiweeks import Week

            EW = str(int(x.EW))
            EW = Week( int(EW[:4]), int(EW[-2:]) )
            
            x["MW"] = self.fromEW2ME(EW)
            return x
        self.ushospdata = ushospdata.apply(addMWWeek ,1)

    def fromEW2ME(self,EW):
        from epiweeks import Week
        RW = Week.fromdate(pd.to_datetime("1970-01-01"))
        n = 0
        while RW < EW:
            RW = RW+1
            n+=1
        return n-1
        
    def numNewHospsUS(self):
        EWs = self.ushospdata.EW
        MWs = self.ushospdata.MW

        self.ushospdata['adultAndChildDeaths'] = self.ushospdata.previous_day_admission_adult_covid_confirmed + self.ushospdata.previous_day_admission_pediatric_covid_confirmed
        newHosps = self.ushospdata.adultAndChildDeaths.diff()
        return (EWs,MWs,newHosps) 

def computeYticks(ys):
    ys = ys[~np.isnan(ys)]
    miny,maxy = min(ys),max(ys)
    return [int(y) for y in np.linspace( miny,maxy,10)]
    
if __name__ == "__main__":

    hospData = dhsHosp()
    EWs, MWs, numNewHospInUS = hospData.numNewHospsUS()
    EWs, MWs, numNewHospInUS  = EWs[:-1], MWs[:-1] , numNewHospInUS[:-1]

    # - plot the data
    plt.style.use("fivethirtyeight")
    
    fig,ax = plt.subplots()
    ax.scatter( MWs, numNewHospInUS,s=20 )
    ax.plot( MWs, numNewHospInUS, lw=3.,alpha=0.50 )

    ax.set_xticks(MWs[::5])
    ax.set_xticklabels( [int(x) for x in EWs[::5]] )
    
    ax.tick_params(which="both",labelsize=8)

    ax.set_xlabel("Epiweek", fontsize=10)
    ax.set_ylabel("Num. of previous day adult and child admissions\n to a US hosp. who had confirmed COVID-19", fontsize=10)

    ax.text(0.01, 0.99, "Data as recent as {:s}".format( hospData.metaDataDict['revision_timestamp'] )
            ,weight="bold",fontsize=10,ha="left",va="top", color="#3d3d3d",transform=ax.transAxes)
    
    ax.set_yticks( computeYticks(numNewHospInUS) ) 
    ax.set_yticklabels(["{:,}".format(y) for y in ax.get_yticks()])
                   
    fig.set_tight_layout(True)

    w = mm2inch(189)
    fig.set_size_inches(w,w/1.6)
    
    plt.savefig("numbewOfNewHospitlizations.png")
    plt.close()
