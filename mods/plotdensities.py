#mcandrew, luk, codi

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import seaborn as sns

from textwrap import wrap

sys.path.append('../')
from mods.plothelp import savefig
from mods.datahelp import grabData


def densityPlot(dataset,qid,outputFilename): #<- i think these are the only inputs we will need? If not, add more.
    
    #qid = 6163 #metaculus question number, this is from single plot code (now passed in as parameter)

    #reading in the csv files
    gd = grabData("../data")
    #totalData = gd.predictions() #this was from single plot code, (have dataset parameter now)
    quantiles = gd.quantiles()
    questData = gd.questions()

    #subset to the question we want
    #qidData = totalData[ (totalData.qid == qid)] #from single plot code (have dataset parameter now)
    qidQuan = quantiles[ (quantiles.qid == qid)]

    qidQuan = qidQuan.set_index('quantile') #added to automate indexing by quantile
    questData = questData.set_index('metaculusQuestionNumber')

    plt.style.use('fivethirtyeight')
    fig,ax = plt.subplots()

    for bin, data in dataset.groupby(['qid']):
        ax.plot(data.bin.values, data.dens.values, linewidth = 2, alpha = 0.55)
        ax.fill_between(data.bin.values, data.dens.values, linewidth = 2, alpha = 0.55, color = "skyblue")

    ax.set_title("\n".join(wrap(questData.loc[qid, 'headlineText'], 80)), fontsize = 10)

    ax.tick_params(which='both',labelsize=8)

    ax.set_ylabel('Probability Density Function',fontsize=8,color="#2d2d2d")

    densityAnnots = gd.densityAnnots().set_index("qid")
    ax.set_xlabel(densityAnnots.loc[qid,"xlabel"],fontsize=8,color="#2d2d2d") 
    ax.ticklabel_format(useOffset=False,style='plain')
    ax.set_xticks(np.arange(densityAnnots.loc[qid, "xBegin"], densityAnnots.loc[qid, "xEnd"]+1, densityAnnots.loc[qid, "xBy"])) #added for x axis formatting
    
    if(qid != 6163): #rounding issues with 6163, adding .2f made it harder to read the rest of the plots
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    #variables for the percentiles
    ten    = qidQuan.loc['0.1', 'value'] #10th percentile
    fifty  = qidQuan.loc['0.5', 'value'] #50th percentile
    ninety = qidQuan.loc['0.9', 'value'] #90th percentile

    #the corresponding density values for each percentile
    dataset = dataset.set_index('bin')
    tenDens = dataset.loc[ten, 'dens']
    fiftyDens = dataset.loc[fifty, 'dens']
    ninetyDens = dataset.loc[ninety, 'dens']

    #labeling the percentiles
    ax.plot( [ten]*2, [0,tenDens], linestyle= "--", linewidth = 2,color = "k")
    ax.plot( [fifty]*2, [0,fiftyDens], linestyle= "--", linewidth = 2,color = "k")
    ax.plot( [ninety]*2, [0,ninetyDens], linestyle= "--", linewidth = 2,color = "k")

    #labeling the three quantiles
    ymin,ymax = ax.get_ylim()
    yRange    = ymax-ymin
    txt10 = "10th percentile: {0:,.2f}".format(ten)
    txt50 = "50th pecentile: {:,.2f}".format(fifty)
    txt90 = "90th percentile: {:,.2f}".format(ninety)

    def densAnnot(x,y,s,va,ha,ax):
        ax.text(x,y,s,ha=ha,va=va,fontsize=8,color="k",weight="bold")

    densAnnot(x = ten*(1-0.025),y = tenDens,s = txt10,va="top",ha="right",ax=ax)
    densAnnot(x = fifty*1.025  , y = fiftyDens, s = txt50, va = "top", ha = "left",ax=ax)
    densAnnot( x = ninety*1.025, y = ninetyDens*1.025, s = txt90, va = "top", ha = "left",ax=ax)

    # small table of stats
    surveyNum = questData.loc[qid,"surveyNumber"]

    metaData = gd.metaData().set_index(["qid"])
    nPredictions = metaData.loc[ qid,"numOfPredictions"]

    launchDate,closeDate = questData.loc[qid,'launchDate'], questData.loc[qid,'closeDate']
    txts = ["Survey Number = {:02d}".format(surveyNum), "Forecasting period = {:s} to {:s}".format(launchDate,closeDate),  "Number of predictions = {:d}".format(nPredictions) ]
    
    # get table printing info from DensityAnnots.csv
    x, y, lr = densityAnnots.loc[qid, 'tableX'], densityAnnots.loc[qid, 'tableY'], densityAnnots.loc[qid, 'align']

    for i,txt in enumerate(txts):
        ax.text(x,y-i*0.05, txt , color="k",weight="bold",fontsize=8,transform=ax.transAxes,ha=lr)
    
    fig.set_tight_layout(True)
    savefig(fig,w=183,filename="./densityplots/" + outputFilename.format(qid))

if __name__ == "__main__":
    pass



