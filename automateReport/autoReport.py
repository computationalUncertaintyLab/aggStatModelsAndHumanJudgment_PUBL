#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import pickle

class automateReport(object):
    def __init__(self,root,texin,fout):
        import os
        self.root  = root
        self.texin = os.path.join(root,texin)
        self.fout  = open(os.path.join(root,fout),"w")

        self.loadReportDataDictionary()

    def fillintex(self):
        for line in open(self.texin,"r"):
            filledInLine = line
            for key,val in self.reportData.items():
                strKey   = [str(k) for k in key[:-1]]

                if key[-1] == "comma":
                    strValue = "{:,}".format(int(val))
                if key[-1] == "1":
                    strValue = "{:.1f}".format(val)
                if key[-1] == "2":
                    strValue = "{:.2f}".format(val)
                if key[-1] == "d":
                    strValue = "{:d}".format(val)
                if key[-1] == "s":
                    strValue = "{:s}".format(val)
                    
                filledInLine = filledInLine.replace("{{"+",".join(strKey)+"}}",strValue)
            self.fout.write(filledInLine)
        self.fout.close()
        
    def loadReportDataDictionary(self):
        import pickle
        self.reportData = pickle.load(open("../data/reportData.pkl","rb"))

if __name__ == "__main__":

    autoport = automateReport("../summaryreports/summaryReport01/","main.tex","autorReport01.tex")
    autoport.fillintex()
