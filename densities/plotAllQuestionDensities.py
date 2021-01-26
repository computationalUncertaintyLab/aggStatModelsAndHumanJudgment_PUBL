#mcandrew, luk

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


sys.path.append('../')

from mods.plotdensities import densityPlot
from mods.datahelp import grabData

if __name__ == "__main__":

    gd = grabData("../data")
    qData = gd.questions()
    predictions = gd.predictions()
    
    for (qid,subset) in predictions.groupby(["qid"]):
        print("Plotting density for question {:d}".format(int(qid)))
        densityPlot(dataset=subset, qid=qid,outputFilename="consensusDensity__{:05d}.eps".format(qid))
