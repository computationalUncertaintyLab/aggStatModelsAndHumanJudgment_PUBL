#mcandrew

import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

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
        newHosps = self.ushospdata.total_adult_patients_hospitalized_confirmed_and_suspected_covid.diff()
        return (EWs,MWs,newHosps) 

if __name__ == "__main__":

    hospData = dhsHosp()
    EWs, MWs, numNewHospInUS = hospData.numNewHospsUS()

    plt.style.use("fivethirtyeight")
    
    fig,ax = plt.subplots()
    ax.scatter( MWs, numNewHospInUS )
    ax.plot( MWs, numNewHospInUS, lw=3. )

    ax.set_xticks(MWs[::5])
    ax.set_xticklabels( [int(x) for x in EWs[::5]] )
    
    ax.tick_params(which="both",labelsize=6)

    ax.set_xlabel("Epiweek", fontsize=10)
    ax.set_ylabel("Number of new US hospitilizations", fontsize=10)
    
    plt.show()
