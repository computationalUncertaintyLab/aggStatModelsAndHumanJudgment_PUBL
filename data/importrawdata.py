#mcandrew

import sys
import numpy as np
import pandas as pd

class mVaccTherQuestions(object):
    def __init__(self,loginfile):
        self.importLoginInfo(loginfile)
        
    def importLoginInfo(self,loginfile):
        loginInfo = {}
        for line in open(loginfile):
            k,v = line.strip().split(",")
            loginInfo[k] = v
        self.username  = loginInfo['username']
        self.password  = loginInfo['password']
        self.csrftoken = loginInfo['csrftoken']

    def sendRequest2Server(self):
        import requests
        client = requests.session() # start session
    
        # add CSRF cookie
        cookie_obj = requests.cookies.create_cookie(name="csrftoken",value= self.csrftoken)
        client.cookies.set_cookie(cookie_obj)

        # add headers
        headers = { "referer":"https://covid.metaculus.com/questions/"
                    ,'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
                    ,'accept': 'application/json; version=LATEST'
        }
        client.headers.update(headers)
        
        # post username and password to form to authenticate
        payload = {
	    "username": self.username, 
	    "password": self.password,
        }
        p = client.post("https://pandemic.metaculus.com/api2/accounts/login/", data = payload)
        self.client = client
        self.auth   = p

    def collectQdata(self,QN):
        root = "https://pandemic.metaculus.com/api2/questions/{:d}"
        data = self.client.get(root.format(QN)).json()
        self.data = data

    def constructPDF(self):
        density = self.data['community_prediction']['unweighted']['y']
        numProbs = 200
        
        minvalue  = self.data['possibilities']['scale']['min']
        maxvalue  = self.data['possibilities']['scale']['max']

        self.minvalue = minvalue
        self.maxvalue = maxvalue
        
        if type(minvalue) is int:
            minvalue = float(minvalue)
            maxvalue = float(maxvalue)
        elif "-" in minvalue:
            minvalue = pd.to_datetime(minvalue)
            maxvalue = pd.to_datetime(maxvalue)
        interval = (maxvalue-minvalue)/numProbs
        
        xs = [minvalue]
        for _ in range(numProbs):
            xs.append(xs[-1]+interval)
        self.xs=xs
        self.dens=density
        self.interval = interval

    def hasDist(self):
        try:
            density = self.data['community_prediction']['unweighted']['y']
            return 1
        except:
            return 0

def addInCDF(data):
    def cuumsum(x):
        x = x.sort_values('bin')
        x['cdf'] = np.cumsum(x.prob*x.interval)
        return x
    return data.groupby('qid').apply(cuumsum).drop(columns=['qid']).reset_index()

def addInProbs(data):
    def computeProbAndCProb(x):
        import scipy.integrate as integrate

        if np.issubdtype(data.bin.values[0].dtype, np.datetime64):
            referencetime = pd.to_datetime("2000-01-01")
            xs = [ (x - referencetime).total_seconds()  for x in x.bin.values]
        else:
            xs = [float(x) for x in x.bin.values]
        totalSeconds = (xs[-2] - xs[0])
           
        ys = [float(y) for y in x.dens.values]

        cprobsSimp = [0]
        for i in np.arange(1,200+1):
            cdfSimp = integrate.simps( ys[:i+1], xs[:i+1] ) / totalSeconds
            cprobsSimp.append(cdfSimp)
       #cprobsSimp.append(1.)

        #print(cprobsSimp)
        x['cprobs'] = cprobsSimp
            
        return x
    return data.groupby(['qid']).apply(computeProbAndCProb).reset_index()

if __name__ == "__main__":

    qdata = {'surveynum':[],'numOfPredictions':[],'question':[],'qid':[],'publishtime':[],'closetime':[],'numcomments':[],'numvotes':[]}
    data = {'surveynum':[],'qid':[],'bin':[],'interval':[],'dens':[]}
    
    fromsurveyNumber2Questionlist = {1:[6163,6164,6166,6165,6161,6162,6160]}
                                    #2:[question numbers in list]
    
    for surveyNum,questions in fromsurveyNumber2Questionlist.items():
        metac = mVaccTherQuestions("../../../../../metaculusloginInfo.text")
        metac.sendRequest2Server() # ping the server

        for q in questions:
            sys.stdout.write('\rDownloading data from Q {:04d} and Survey {:02d}\r'.format(q,surveyNum))
            sys.stdout.flush()
            
            metac.collectQdata(q) # collect json data for this specific question
            
            if metac.hasDist() == False: # skip question with textual answers only
                continue
            metac.constructPDF()  # contstuct community, unweighted consensus PDF

            qid = metac.data['id']
            qdata['qid'].append(qid)

            qdata['surveynum'].append(surveyNum)
            
            npredics = metac.data['number_of_predictions']
            qdata['numOfPredictions'].append(npredics)
            
            questionText = metac.data['title'] 
            qdata['question'].append(questionText)

            pubbed = metac.data['publish_time']
            qdata['publishtime'].append(pubbed)
            
            closed = metac.data['close_time']
            qdata['closetime'].append(closed)

            ncomments = metac.data['comment_count']
            qdata['numcomments'].append(ncomments)

            nvotes =  metac.data['votes']
            qdata['numvotes'].append(nvotes)

            interv = metac.interval
            for (x,p) in zip(metac.xs,metac.dens):
                data['qid'].append(qid)
                data['bin'].append(x)
                data['dens'].append(p)
                data['interval'].append(interv)
                data['surveynum'].append(surveyNum)

    # transform dict to a data frame
    qdata = pd.DataFrame(qdata)
    data  = pd.DataFrame(data)

    # approximate density to compute probs
    data = addInProbs(data)
    data = data.drop(columns=["index"])

    # store data
    from datetime import datetime
    today = datetime.today()
    
    qdata.to_csv("./metaData.csv",index=False)
    data.to_csv("./predictiondata__{:04d}-{:02d}-{:02d}.csv".format(today.year,today.month,today.day),index=False)
