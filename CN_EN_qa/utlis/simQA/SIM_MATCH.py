import json
import numpy as np
import time
import jieba
from jieba import analyse
import os


def create_vec_dict(file_path):
    file = open(file_path, "r")
    lines = file.readlines()
    vecs_dic = {}
    for line in lines:
        li = line.strip().split()
        vec = [float(ele) for ele in li[1:]]
        vecs_dic[li[0]] = vec
    return vecs_dic

def sent2vec(sent, vecs_dic):
    "Turn a sentence into a vector."
    sent_vecs = []
    tokenizer = jieba.dt
    words = tokenizer.cut(sent.strip())
    words_set = set(words)
    word_weight_dic = {}
    for word in words_set:
        word_weight_dic[word] = 1
    word_weight_pairs = analyse.extract_tags(sent, withWeight=True)
    for word_weight in word_weight_pairs:
        word = word_weight[0]
        weight = word_weight[1]
        word_weight_dic[word] = weight
    for key in word_weight_dic.keys():
        try:
            weighted_vec = np.array(vecs_dic[key])*word_weight_dic[key]
            sent_vecs.append(weighted_vec)
        except:
            sent_vecs.append(np.zeros(300))
    vec = np.sum(sent_vecs, axis=0)
    return vec

def main_cache(file_path,vecs_dic):
    file = open(file_path, "r")
    lines = file.readlines()
    vecs = []
    l2_norms = []
    answers = []
    questions = []
    for line in lines:
        dic = eval(line.strip())
        question = dic['question']
        vec = sent2vec(question,vecs_dic)
        l2_norm = np.linalg.norm(vec)
        # 当l2_norm=0时无法计算 cosine similarity，所以要跳过这样的问题，进入下一个问题的处理
        if l2_norm == np.zeros(1)[0]:
            continue
        vecs.append(vec)
        l2_norms.append(l2_norm)
        answers.append(dic['answers'])
        questions.append(question)
    vecs = np.mat(vecs)
    l2_norms = np.array(l2_norms)
    return vecs, l2_norms, answers, questions

def compute_similarities(mat, vec, denominators):
    '''
    Calculate the cosine similarities between the input question
    and the questions already in the cache.
    '''
    mat1 = np.reshape(vec, (300,1))
    mat1 = np.mat(mat1)
    numerators = np.matmul(mat, mat1)
    similarities = []
    numerators = np.reshape(numerators, (numerators.shape[0],))
    similarities = numerators/denominators
    return similarities

def semantics_matching(question):
    startPoint = time.time()
    vec = sent2vec(question, vecs_dic)
    denominators = np.linalg.norm(vec)*l2_norms
    similarities = compute_similarities(vecs, vec, denominators)
    index = np.argmax(similarities)
    similarities = np.array(similarities)
    # print (type(similarities))
    # print (similarities[0])
    score = similarities[0][index]
    endPoint = time.time()
    print ('The process time is: ', str(endPoint-startPoint))
    return questions[index], answers[index], score

'''que1 = '广州有什么好玩的？'
que2 = '端午节是为了纪念谁？'
que3 = '中华人民共和国在哪一年成立？'
que4 = '范冰冰的身高是？'
que5 = '“认识你自己”是哪位哲学家说的？'

que6 = '资本论的作者是？'
que7 = '商鞅是怎么死的？'

que8 = '阿胶的制作方法？'
que9 = '黄家驹的作品有哪些？'
que10 = '刘亦菲主演过哪些电视剧？'
'''

CN_EN_QA_DATA_PATH = os.getenv('CN_EN_QA_DATA_PATH')
baike_vectors_path = os.path.join(CN_EN_QA_DATA_PATH, 'baidubaike')
baidu_factoids_path = os.path.join(CN_EN_QA_DATA_PATH, 'baidu_factoid_qa_pairs.json')
vecs_dic = create_vec_dict(baike_vectors_path)
vecs, l2_norms, answers, questions = main_cache(baidu_factoids_path, vecs_dic)

'''ques = [que1, que2, que3, que4, que5, que6, que7, que8, que9, que10]
for que in ques:
    similar_question, ans, score = semantics_matching(que)
    # print ('The most similar question to the input question is: ', similar_question)
    # print ('The answers are: ', ans)
    print ('The score for the answer is: ', score)
'''





