#mcandrew

import sys
sys.path.append("../")

from mods.compareAndCmbineEnsembles import ensembleCombiner

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
   
if __name__ == "__main__":

    for idx,row in pd.read_csv("ensembleComparisonData.csv").iterrows():
        ec = ensembleCombiner(row)
        covidhubQuantiles = ec.grabCOVIDHUBdata()
        crowdQuantiles    = ec.grabConsensusData()
        
        covidhubAndCrowd = ec.buildQuantileAvgsMetaForecast()
   
        ec.generatePlot()
