#!/usr/bin/env python3
"""A script to run the URun QA reader model interactively."""


from drqa.reader import Predictor 
import time
import prettytable

reader_path = "/home/jiangwei/Projects/URun.ResearchPrototype/Projects/DrQA/data/reader/single.mdl"
 
predictor = Predictor(model=reader_path, num_workers=0)

def knowAll(atcPaths):
     doc=''
     for path in atcPaths:
         f = open(path,"r")
         doc ='\n'+f.read()
     return doc
 
atcPaths=[]
atcPaths.append('/home/haiyun/URun.ResearchPrototype/Projects/VoiceTranslator/utlis/qaDocuments/1.article')
atcPaths.append('/home/haiyun/URun.ResearchPrototype/Projects/VoiceTranslator/utlis/qaDocuments/2.article')
document= knowAll(atcPaths)

def process(question, candidates=None, top_n=1):
      t0 = time.time()
      predictions = predictor.predict(document, question, candidates, top_n)
      table = prettytable.PrettyTable(['Rank', 'Span', 'Score'])
      for i, p in enumerate(predictions, 1):
          table.add_row([i, p[0], p[1]])
      print(table)
      print('Time: %.4f' % (time.time() - t0)) 
      return p[0]                                         


 

