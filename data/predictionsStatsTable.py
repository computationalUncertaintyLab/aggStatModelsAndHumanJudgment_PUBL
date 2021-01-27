#mcandrew

import sys
import numpy as np
import pandas as pd

sys.path.append("../")
from mods.datahelp import grabData

def computeMedianAndIQR(d):

    stats = {"quantile":[], "value":[]}
    for quantile in [ 0.010, 0.025, 0.050, 0.100, 0.150, 0.200
                      ,0.250, 0.300, 0.350, 0.400, 0.450, 0.500, 0.550, 0.600
                      , 0.650 ,0.700 ,0.750 ,0.800 ,0.850 ,0.900 ,0.950
                      ,0.975, 0.990 ]:
        d["distanceFromQ"] = abs(d.cprobs - quantile)
        val = d.sort_values("distanceFromQ").iloc[0]["bin"]

        stats["quantile"].append(quantile)
        stats["value"].append(val)

    # add in mode
    stats["quantile"].append("mode")
    stats["value"].append( d.sort_values("dens").iloc[-2]["bin"] )
    
    return pd.DataFrame(stats)
  
if __name__ == "__main__":

    """ This code produces quantiles from predictive consensus distributions for each question asked that required a quantitiative output.
    """

    n=0
    gd = grabData("../data")
    predictions = gd.predictions()
    
    for (surveynum,qid),data in predictions.groupby(["surveynum","qid"]):
        print(qid)

        stats = computeMedianAndIQR(data)
        stats['surveynum'] = surveynum
        stats['qid'] = qid

        if n==0:
            H=True
            M="w"
            n=1
        else:
            H=False
            M="a"
        stats.to_csv("./quantilesFromConsensusPredictions.csv",mode=M,header=H,index=False)
