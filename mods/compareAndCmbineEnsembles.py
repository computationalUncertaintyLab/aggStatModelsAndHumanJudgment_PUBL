#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class ensembleCombiner(object):
    def __init__(self,data):
        self.target = data.target
        self.qid    = data.qid
        self.startdate, self.enddate = data[["startdate","enddate"]]

        self.plotname    = data.plotname
        self.targetlabel = data.targetlabel.replace("\\n","\n")
        
    def grabCOVIDHUBdata(self):
        from mods.datahelp import grabCOVIDHUBensemble
        
        hub = grabCOVIDHUBensemble("../data")
        
        covidhub = hub.subset2nat()
        covidhubCases  = covidhub.subsettarget(self.target)

        covidhubCases  = covidhubCases.subset2targetdate(self.enddate).subset2forecastdate(self.startdate).grabData()
        covidhubCases  = covidhubCases.loc[covidhubCases["type"]=="quantile",:] # quantiles only, not points

        covidhubCases.set_index(["quantile"],inplace=True)
        covidhubCases = covidhubCases.rename(columns={"value":"hubvalue"})

        self.covidhubCases = covidhubCases
        return covidhubCases

    def grabConsensusData(self):
        from mods.datahelp import grabData
        crowd = grabData("../data")

        quantiles = crowd.quantiles()
        quantiles = quantiles.loc[quantiles["quantile"]!="mode",:]
        quantiles["quantile"] = quantiles["quantile"].astype(float)
        quantiles = quantiles.loc[quantiles.qid==self.qid,:].set_index("quantile")
        quantiles = quantiles.rename(columns={"value":"crowdvalue"})

        self.crowdQuantiles = quantiles
        return quantiles

    def buildQuantileAvgsMetaForecast(self):
        covidhubAndCrowd = self.covidhubCases.merge(self.crowdQuantiles, left_index=True, right_index=True)
        covidhubAndCrowd["metavalue"] = (covidhubAndCrowd.hubvalue+covidhubAndCrowd.crowdvalue)/2.
        self.covidhubAndCrowd = covidhubAndCrowd
        return covidhubAndCrowd

    def generatePlot(self):
        import matplotlib.ticker as mtick
        from mods.plothelp import mm2inch,savefig
        
        def uniformcf(x,a,b):
            return (x-a)/(b-a)

        def plotCdf(d,val,col,label):
            
            def interp(xs,ys):
                from scipy.interpolate import interp1d
                f = interp1d(xs, ys,  kind='linear')
    
                xs = np.linspace(min(xs),max(xs),10**3)
                return xs,f(xs)

            def fromcdf2pdf(xs,ps):
                avgxs = []
                for (x0,x1) in zip(xs,xs[1:]):
                    avgxs.append(0.5*(x0+x1))
                pdfvals = np.diff(ps)
                return avgxs,pdfvals
            
            cdfxs,cdfvals = interp(d[val],d.index)
            pdfxs,pdfvals = fromcdf2pdf(cdfxs,cdfvals)

            ax.plot(cdfxs,cdfvals, lw=2, alpha=0.60,color=col, label=label )
            ax.scatter( d[val], d.index, s=10,color=col )

        def plotUniformCDF(ax):
            xmin,xmax = ax.get_xlim()
            domain = np.linspace(xmin,xmax,5)
            ax.plot(domain,uniformcf(domain,xmin,xmax),color="k",alpha=0.50,linestyle="--",lw=1)

        def plotBoxPl(d,val,col,xpos):
            ax.plot( [xpos,xpos], [ d.loc[0.1,val], d.loc[0.9,val]]  , lw=15,alpha=0.50,color=col)
            ax.plot( [xpos,xpos], [ d.loc[0.25,val], d.loc[0.75,val]], color="k", lw=2.5,alpha=0.75)
            ax.scatter( [xpos], d.loc[0.50,val], s=30,color="k", alpha=1)
        
        # -- code to plot
        plt.style.use("fivethirtyeight")
    
        fig,axs = plt.subplots(1,2)

        ax = axs[0]
        labels = ["COVIDHub\nensemble","Crowd\nensemble","Metaforecast"]
        for val,col,label in zip(["hubvalue","crowdvalue","metavalue"],["blue","red","purple"],labels):
            plotCdf(self.covidhubAndCrowd,val,col,label)
        plotUniformCDF(ax)
        ax.legend(frameon=False,loc="upper left",fontsize=8)

        ax.set_xlabel(self.targetlabel,fontsize=10)
        ax.set_ylabel(r"Cumulative density $P(X<x)$",fontsize=10)

        ax.tick_params(which="both",labelsize=8)

        xticks = ax.get_xticks()

        if xticks[-1] > 10**6:
            ax.set_xticklabels([ "{:.1f}M".format(x/10**6) for x in xticks])
        elif xticks[0] > 10**3:
            ax.set_xticklabels([ "{:.1f}K".format(x/10**3) for x in xticks])
            
        ax = axs[1]

        for val,col,xpos in zip(["hubvalue","crowdvalue","metavalue"],["blue","red","purple"],[0,1,2]):
            plotBoxPl(self.covidhubAndCrowd,val,col,xpos)

            if xpos==0:
                ax.text(0,self.covidhubAndCrowd.loc[0.10,val],s="10th pct",ha="center",va="top",weight="bold",fontsize=8)
                ax.text(0,self.covidhubAndCrowd.loc[0.90,val],s="90th pct",ha="center",va="bottom",weight="bold",fontsize=8)

                ax.text(0.15,self.covidhubAndCrowd.loc[0.25,val],s="25th pct",ha="left",va="center",weight="bold",fontsize=8)
                yval = self.covidhubAndCrowd.loc[0.25,val]
                ax.plot([0.15,0],[yval,yval*1.0025] ,color="k",lw=1)

                ax.text(0.15,self.covidhubAndCrowd.loc[0.75,val],s="75th pct",ha="left",va="center",weight="bold",fontsize=8)
                yval = self.covidhubAndCrowd.loc[0.75,val]
                ax.plot([0.15,0],[yval*1.0025,yval] ,color="k",lw=1)

                ax.text(0.15,self.covidhubAndCrowd.loc[0.50,val],s="Median",ha="left",va="center",weight="bold",fontsize=8)
                ax.plot([0.15,0],[self.covidhubAndCrowd.loc[0.50,val]]*2,color="k",lw=1)

        ax.set_xticks([0,1,2])
        ax.set_xlim(-0.5,2.5)

        ax.set_xticklabels(labels)
        ax.tick_params(which="both",labelsize=8)

        ax.set_ylabel(self.targetlabel,fontsize=10)
        ax.set_xlabel("")

        ax.set_yticks(xticks[1:-1])

        ylimMin,ylimMax = ax.get_ylim()
        ax.set_ylim(ylimMin*0.99, ylimMax*1.01)

        ax.get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

        fig.set_tight_layout(True)
        savefig(fig,"{:s}".format(self.plotname),183)
        
if __name__ == "__main__":
    pass



    
    

