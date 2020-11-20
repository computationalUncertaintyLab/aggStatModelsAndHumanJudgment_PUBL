#mcandrew

import sys
import numpy as np
import pandas as pd

class dhsHosp(object):
    def __init__(self):
        import pandas as pd
        self.grabMetaData()
        self.loadData()

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
            dataUrl =   self.metaDataDict['resources'][0]['url']
            self.hospdata = pd.read_csv(dataUrl)
        except:
            print("Error downloading data")

if __name__ == "__main__":

    hospData = dhsHosp()
    print(hospData.hospdata)
    

