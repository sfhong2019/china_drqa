#!/usr/bin/env python3
# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import torch
import argparse
import code
import prettytable
import logging

from termcolor import colored
from drqa import pipeline
from drqa.retriever import utils
import sys
import os
from configuration import arguments
import time

global DrQA

args={}
args['reader model'] = arguments.reader 
args['retriever model'] = arguments.retriever
args['doc db'] = [arguments.doc_db]
args['candidate files'] = arguments.candidate_files
args['no cuda'] = arguments.no_cuda
args['gpu'] = arguments.gpu
args['tokenizer'] = arguments.tokenizer

# print(args['reader model'])
# print (args['retriever model'])
# print (args['candidate files'])
# print (args['doc db'])
# print(args['no cuda'])
# print (args['gpu'])
# print (args['tokenizer'])


cuda_available = not args['no cuda'] and torch.cuda.is_available()
if cuda_available:
    torch.cuda.set_device(args['gpu'])
    print ('CUDA enabled (GPU %d)' % args['gpu'])
else:
    print ('Running on CPU only.')

if args['candidate files']:
    print ('Loading candidates from %s' % args.candidate_file)
    candidates = set()
    with open(args.candidate_file) as f:
        for line in f:
            line = utils.normalize(line.strip()).lower()
            candidates.add(line)
    print ('Loaded %d candidates.' % len(candidates))
else:
    candidates = None


cuda=cuda_available
fixed_candidates=candidates
reader_model=args['reader model']
ranker_config={'options': {'tfidf_path': args['retriever model']}}
tokenizer=args['tokenizer']
en_db = {'options': {'db_path': args['doc db'][0]}}
# cn_db = {'options': {'db_path': args['doc db'][1]}}

print ('Begin to run on the pipeline!')
ENDrQA = pipeline.DrQA(cuda=cuda, fixed_candidates=fixed_candidates, reader_model=reader_model, ranker_config=ranker_config, db_config=en_db, tokenizer=tokenizer)
print ('Finish running on the pipeline!')
# CNDrQA = pipeline.DrQA(cuda=cuda, fixed_candidates=fixed_candidates, reader_model=reader_model, ranker_config=ranker_config, db_config=cn_db, tokenizer=tokenizer)

def fbqa(question, knowledge_source, candidates=None, top_n=1, n_docs=5):
    if knowledge_source == 'en_wikipedia':
        predictions = ENDrQA.process(question, candidates, top_n, n_docs, return_context=False)
    elif knowledge_source == 'cn_wikipedia':
        predictions = CNDrQA.process(question, candidates, top_n, n_docs, return_context=False)
    else:
        return 'knowledge source error!'
    for p in predictions:
            return p['span']

'''question1 = 'Who is the first black president of America?'
question2 = 'who is the first black president of America?'
question3 = 'When is chrismas?'
question4 = 'when is chrismas?'
question5 = 'When is Chrismas?'
question6 = 'What is question answering?'
question7 = 'what is question answering?'
questionList = [question1,question2,question3,question4,question5,question6,question7]
for question in questionList:
    start = time.time()
    print (fbqa(question,'en_wikipedia'))
    end = time.time()
    print ('The process time is:', end-start)
'''



    


    

    
    



