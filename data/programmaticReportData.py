#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("../")
from mods.datahelp import grabData, grabJHUData, grabDHSdata

class reportBuilder(object):
    def __init__(self,gd):
        self.predictions = gd.predictions()
        self.qData       = gd.questions()
        self.quantiles   = gd.quantiles()
        self.metaData    = gd.metaData()

    def buildConsensusAndMedianPredictionText(self):
        fromSurveyNumQidTXT2data = {}
        for (surveyNum,qid),subset in self.quantiles.groupby(["surveynum","qid"]):
            subset = subset.set_index(["quantile"])

            median   = subset.loc["0.5","value"]
            _10thPct = subset.loc["0.1","value"]
            _90thPct = subset.loc["0.9","value"]
            
            if _10thPct > 10:
                form="comma"
            elif _10thPct >1:
                form="1"
            else:
                form="2"
            
            fromSurveyNumQidTXT2data[surveyNum,qid,"median",form] = median
            fromSurveyNumQidTXT2data[surveyNum,qid,"_10",form]    = _10thPct
            fromSurveyNumQidTXT2data[surveyNum,qid,"_90",form]    = _90thPct
        self.reportDict = fromSurveyNumQidTXT2data

    def addJHUdata(self,jhudata):
        jhudata = jhudata.set_index(pd.to_datetime(jhudata.index))
        mostRecentJhudata = jhudata.sort_index().iloc[-1,:]
        dataDate = pd.to_datetime(mostRecentJhudata.name)
        
        self.reportDict[-1,-1,"jhuday","d"]    = dataDate.day 
        self.reportDict[-1,-1,"jhumonth","s"]  = self.fromint2month(dataDate.month)
        self.reportDict[-1,-1,"jhuyear","d"]   = dataDate.year 

        self.reportDict[-1,-1,"jhucases","comma"]  = mostRecentJhudata.cases 
        self.reportDict[-1,-1,"jhudeaths","comma"] = mostRecentJhudata.deaths

    def addDHSdata(self,dhsData):
        dhsData = dhsData.set_index("date")
        mostRecentdata = dhsData.sort_index().iloc[-1,:]
        dataDate = pd.to_datetime(mostRecentdata.name)

        self.reportDict[-1,-1,"dhsday","d"]    = dataDate.day 
        self.reportDict[-1,-1,"dhsmonth","s"]  = self.fromint2month(dataDate.month)
        self.reportDict[-1,-1,"dhsyear","d"]   = dataDate.year 

        self.reportDict[-1,-1,"dhshosps","comma"]  = mostRecentdata.adultAndChildHosps 

    def fromint2month(self,x):
        int2month = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"June",7:"July",8:"Aug",9:"Sept",10:"Oct",11:"Nov",12:"Dec"}
        return int2month[x]
        
    def pickleReportData(self):
        import pickle
        pickle.dump( self.reportDict, open("./reportData.pkl","wb"))

def aggregateCasesAndDeathsData(jhudata):
     d = jhuData.deathdata.loc[:, ["FIPS"] + [x for x in jhuData.deathdata.columns if "/" in x] ]
     d = d.melt(id_vars=["FIPS"]).rename(columns={"variable":'day',"value":"deaths"})

     c = jhuData.casesdata.loc[:, ["FIPS"] + [x for x in jhuData.casesdata.columns if "/" in x] ]
     c = c.melt(id_vars=["FIPS"]).rename(columns={"variable":'day',"value":"cases"})

     deathsAndCases = d.merge(c,on = ["FIPS","day"])

     def sumCasesAndDeaths(x):
         deaths = x["deaths"]
         cases  = x["cases"]

         return pd.Series({"cases":sum(cases),"deaths":sum(deaths) })
     deathsAndCasesByDay = deathsAndCases.groupby(["day"]).apply(sumCasesAndDeaths)
     return deathsAndCasesByDay

if __name__ == "__main__":

    gd = grabData("../data")
    jhuData = grabJHUData('../jhudata/')
    deathsAndCases = aggregateCasesAndDeathsData(jhuData)

    dhsData = grabDHSdata().ushospdata
     
    RB = reportBuilder(gd)
    RB.buildConsensusAndMedianPredictionText()

    RB.addJHUdata(deathsAndCases)
    RB.addDHSdata(dhsData)
    
    RB.pickleReportData()
