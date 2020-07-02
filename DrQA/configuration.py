import os

class Config:
    DRQA_DATA_PATH = os.getenv('DRQA_DATA_PATH')
    doc_db = DRQA_DATA_PATH + '/wikipedia/docs.db'
    retriever = DRQA_DATA_PATH + '/wikipedia/docs-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz'
    reader = DRQA_DATA_PATH + '/reader/multitask.mdl'
    candidate_files = None
    no_cuda = False
    gpu  = 0
    tokenizer = 'corenlp'
    
arguments = Config

print (arguments.DRQA_DATA_PATH)
print (arguments.doc_db)
print (arguments.retriever)
print (arguments.reader)
