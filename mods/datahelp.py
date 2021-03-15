#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class grabData(object):
   
    def __init__(self,filepath,latest=1):
       
        self.filepath = filepath
        self.latest=latest

    def quantiles(self):
        from glob import glob
        import os
 
        fl = os.path.join(self.filepath,"quantilesFromConsensusPredictions.csv")
        print("Importing {:s}".format(fl))
        return pd.read_csv(fl)
    
    def predictions(self):
        from glob import glob
        import os
 
        fl = sorted(glob( os.path.join(self.filepath,"predictiondata*.csv")))[-1]
        print("Importing {:s}".format(fl))
        return pd.read_csv(fl)

    def questions(self):
        from glob import glob
        import os
 
        fl = os.path.join(self.filepath,"questionData.csv")
        print("Importing {:s}".format(fl))
        return pd.read_csv(fl)

    def densityAnnots(self):
        import os
 
        fl = os.path.join(self.filepath,"DensityAnnots.csv")
        print("Importing {:s}".format(fl))
        return pd.read_csv(fl)
    
    def metaData(self):
        import os
 
        fl = os.path.join(self.filepath,"metaData.csv")
        print("Importing {:s}".format(fl))
        return pd.read_csv(fl)

class grabJHUData(object):
    def __init__(self,root):
        import os
        self.deathdata = pd.read_csv(os.path.join(root,"csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"))
        self.casesdata = pd.read_csv(os.path.join(root,"csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"))
        print("Importing JHU cases and death data")

class grabDHSdata(object):
    def __init__(self):
        import pandas as pd
        self.grabMetaData() # <- ping API and gran meta data for DHS dataset
        self.loadData()     # <- read data from the DHS website
        self.total()        # <- sum all columns across states for every date

    # - data pull
    def grabMetaData(self):
        import requests
        # TODO this url will be retired entirely soon.. need to migrate the new API format.
        # Until then, the legacy url will continue to be supported for a few weeks. 
        metadata = requests.get("https://legacy.healthdata.gov/api/3/action/package_show?id=83b4a668-9321-4d8c-bc4f-2bef66c49050&page=0")
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
        ushospdata['adultAndChildHosps'] = ushospdata.previous_day_admission_adult_covid_confirmed + ushospdata.previous_day_admission_pediatric_covid_confirmed

        ushospdata = ushospdata.loc[:,["date","adultAndChildHosps"]]
        self.ushospdata = ushospdata
        
class grabRawCOVIDHUBensemble(object):
    def __init__(self):
        self.pullFromGitServer()
        self.aggregateDataAndWriteOut()

    def pullFromGitServer(self):
        import requests
        import re

        ensembleFiles = []
        serverGet = requests.get("https://github.com/reichlab/covid19-forecast-hub/tree/master/data-processed/COVIDhub-ensemble")
        for line in serverGet.iter_lines():
            search = re.search(".*COVIDhub-ensemble.csv",str(line))
            if search:
                hubfile = re.search("\d{4}-\d{2}-\d{2}-COVIDhub-ensemble.csv",str(search.group()))
                ensembleFiles.append(hubfile.group())
        ensembleFiles = sorted(ensembleFiles)
        self.ensembleFiles = ensembleFiles

    def aggregateDataAndWriteOut(self):
        roothtml = "https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-processed/COVIDhub-ensemble/{:s}"
        
        i=1
        for fil in self.ensembleFiles:
            print("Downloading {:s}".format(fil))

            d = pd.read_csv(roothtml.format(fil))
            d = d[["forecast_date","target","target_end_date","location","type","quantile","value"]]
            if i:
                d.to_csv("./COVIDHUBEnsemble.csv", index=False,mode="w") 
                i=0
            else:
                d.to_csv("./COVIDHUBEnsemble.csv", header=False, index=False,mode="a") 
        print("{:d} COVIDHUB files loaded".format(len(self.ensembleFiles)))

class grabCOVIDHUBensemble(object):
    def __init__(self,root):
        import os
        self.covidhub = pd.read_csv(os.path.join(root,"COVIDHUBEnsemble.csv"))
        print("COVIDhub data imported")

    def grabData(self):
        return self.covidhub
        
    def subset2nat(self):
        self.covidhub = self.covidhub.loc[self.covidhub.location=="US",:]
        return self
        
    def subset2forecastdate(self,f):
        self.covidhub = self.covidhub.loc[self.covidhub.forecast_date==f,:]
        return self
    
    def subset2targetdate(self,f):
        self.covidhub = self.covidhub.loc[self.covidhub.target_end_date==f,:]
        return self

    def subsettarget(self,f):
        self.covidhub = self.covidhub.loc[self.covidhub.target.str.contains(f),:]
        return self
    
if __name__ == "__main__":
    pass

    

