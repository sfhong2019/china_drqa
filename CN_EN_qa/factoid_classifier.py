import tensorflow as tf
from nltk.tokenize import word_tokenize
import time
import numpy as np
import os


def vocab2ids(file_path):
        file = open(file_path, 'r')
        lines = file.readlines()
        ids = {}
        flag = 0
        for line in lines:
            items = line.strip().split()
            word = items[1]
            ids[word] = items[0]
        return ids

def get_freqs(file_path):
        '''
        return a dictionary that contains words as keys and the frequencies 
        of the words as values.
        '''
        file = open(file_path, 'r')
        lines = file.readlines()
        freqs = {}
        for line in lines:
            items = line.strip().split()
            # print (items)
            word = items[1]
            freqs[word] = items[2]
        return freqs

def convert2ids(sent, ids, freqs, unknown_lim=20):
        '''
        Convert a sentence into a sequence of indices.

        '''
        ids_li = []
        words = word_tokenize(sent)
        # print (words)
        id_for_unknown = float(len(ids)-1)
        for word in words:
            word = word.lower()
            try:
                # 对于训练集里面出现次数小于unknow_lim的单词，直接将其当做 UNKNOWN WORD
                # print (word)
                # print ('mark0')
                if int(freqs[word]) <= unknown_lim:
                    # print (word)
                    # print (freqs[word])
                    ids_li.append(id_for_unknown)
                else:
                    ids_li.append (float(ids[word]))
            except Exception as e:
                # print (e)
                ids_li.append(id_for_unknown)
        return ids_li

CN_EN_QA_DATA_PATH = os.getenv('CN_EN_QA_DATA_PATH')
vocab_path = CN_EN_QA_DATA_PATH + '/vocab'
ids = vocab2ids(vocab_path)
ids ['UNKNOWNWORD'] = len(ids.keys())
freqs = get_freqs(vocab_path)
global_model = None
#global_graph = None
global_graph = tf.get_default_graph()
maxlen = 60

'''sent ='What is the weather today?'
test_data = convert2ids(sent, ids, freqs)
test_data = tf.keras.preprocessing.sequence.pad_sequences([test_data], padding='post', maxlen=60)
#result = model.predict_classes(test_data)
#print (result)
'''

def classifier(question_list):
    model = tf.keras.models.load_model('./classifier_model.h5')
    x = []
    for question in question_list:
            x.append(convert2ids(question, ids, freqs))
    x = tf.keras.preprocessing.sequence.pad_sequences(x,padding='post',maxlen=maxlen)
    result = model.predict_classes(x)
    return result[0][0]


'''class FactoidClassifier(object):
    def __init__(self):
        self.classifier = 
        self.maxlen = 60
        
    def main(self, question_list):
        # print ('Loading the classifer...')
        # factoid_classifier = tf.keras.models.load_model('./classifier_model.h5')
        # print ('The question list is: ', question_list)
        x = []
        q_preprocess_start = time.time()
        for question in question_list:
            x.append(convert2ids(question, ids, freqs))
        x = tf.keras.preprocessing.sequence.pad_sequences(x,padding='post',maxlen=self.maxlen)
        q_preprocess_end = time.time()
        print ('The time spent in preprocessing the input is: ', str(q_preprocess_end-q_preprocess_start))
        # print ('The input of the model is: ', x)
        # print ('The type of x is: ', type(x))
        print ('The shape of x is: ', x.shape)
        print (x)
        classification_start = time.time()
        with graph.as_default():
            result = self.classifier.predict(x)
        sess = tf.Session(graph=g) # session is run on graph g
        sess.run # run session
        classification_end = time.time()
        print ('The time spent in classification is: ', str(classification_end-classification_start))
        return result
        
cc = FactoidClassifier()
sent ='What is the weather today?'
test_data = convert2ids(sent, ids, freqs)
test_data = tf.keras.preprocessing.sequence.pad_sequences([test_data], padding='post', maxlen=60)
global graph
graph = tf.get_default_graph()
sess = tf.Session(graph=graph)
result = cc.classifier.predict(test_data)

def classify(question):
    global cc
    result = cc.main([question])
    return result[0][0]
‘’‘







def load_model():
    print ('Loading the classifer...')
    factoid_classifier = tf.keras.models.load_model('./classifier_model.h5')
    return factoid_classifier
'''

