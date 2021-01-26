#mcandrew

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def mm2inch(x):
    """this function is used to convert mms to inches for the function fig.set_size_inches in matplotlib.
    """
    return x/25.4

def savefig(fig,filename,w=183):
    w = mm2inch(w)

    fig.set_size_inches(w, w/1.6)
    plt.savefig(filename, dpi=350)
    fig.set_tight_layout(True)
    plt.close()

if __name__ == "__main__":

    pass

