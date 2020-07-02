#/usr/bin/python
#-*- coding:utf-8 -*-

import datetime
import json
import os
import socket

from aip import AipSpeech
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.views.generic import View
import tensorflow as tf

from utlis.translate import MachineTranslation
from utlis.translate import VoiceSynthesizer
from utlis.translate import SpeechRecognition
from utlis.function import delete_excessive_files, text_to_pinyin, dict_get
from factoid_classifier import classifier
from scripts.pipeline.facebookQA import fbqa, ENDrQA
from utlis.simQA.SIM_MATCH import  vecs, l2_norms, answers, questions, semantics_matching
from config import args
import importlib.util
import time

# TODO: 加强代码规范
aip = AipSpeech(args.APP_ID, args.API_KEY, args.SECRET_KEY) # 实例化AipSpeech 

class WebView(View):
    """TTS的web端后端链接

    method: Post
    access_url: http://ip:port/web
    """

    def post(self, request):
        """处理post请求

        Args:
            'text':
            'speedVal':
            'tonesVal':
            'volumeVal':
            'role':
        Returns:
            数据处理后结果，以JSON格式返回
        """
        text = request.POST.get('text', "欢迎使用云润AI开放平台")
        speedVal = request.POST.get('speedVal', 5)
        tonesVal = request.POST.get('tonesVal', 5)
        volumeVal = request.POST.get('volumeVal', 5)
        role = request.POST.get('role', 0)
        start3 = datetime.datetime.now()
        file_url = VoiceSynthesizer(text, speedVal, tonesVal, volumeVal, role, args.file_web_path)
        print("text:", text)
        print("返回的结果:", file_url)
        print("返回的类型:", type(file_url))
        start4 = datetime.datetime.now()
        print(start4 - start3)
        if file_url.strip() == '':
            status = "the audio file is null"
        else:
            status = "ok"
        data = {"audioFileUrl":file_url}
        return HttpResponse(json.dumps({
            "status": status,
            "data":data,
        }))

class MiniProView(View):
    """TTS的微信小程序端后端链接

    method: Post
    access_url: http://ip:port/minipro
    """

    def post(self, request):
        """处理post请求

        Args:
            'text':
            'speedVal':
            'tonesVal':
            'volumeVal':
            'role':
        Returns:
            数据处理后结果, 以JSON格式返回, 返回mp3文件
        """
        # print(request.POST)  # 返回表单所有数据
        # print(request.POST.get('text'))
        # print(request.POST.get('role'))
        # print(request.POST.get('speedVal'))
        # print(request.POST.get('tonesVal'))
        # print(request.POST.get('volumeVal'))
        text2 = request.POST.get('text') # 全部文本
        print(text2)

        speedVal = request.POST.get('speedVal') #
        tonesVal = request.POST.get('tonesVal')
        volumeVal = request.POST.get('volumeVal')
        role = request.POST.get('role')
        options = {}
        options['spd'] = speedVal
        options['pit'] = tonesVal
        options['vol'] = volumeVal
        options['per'] = role

        # file_name = '/Users/ccs/Desktop/DjangoDemoTangdong/static/output/minipro_audio.mp3' # 小程序生成的mp3文件的存放路径
        file_name = './static/output/minipro_audio.mp3' # 小程序生成的mp3文件的存放路径
        # file_name = '/Users/ccs/Desktop/DjangoDemoTangdong/static/output/web_output/'
        # nowTime = datetime.datetime.now().strftime('%Y-%m-%d%&&%H:%M:%S')  # 现在
        # save_file = file_name + "(" + nowTime + ")" + 'web_audio.mp3'
        # # print("文本保存",save_file)
        # num = len([lists for lists in os.listdir(file_name) if os.path.isfile(os.path.join(file_name, lists))])
        # print(num)
        result = aip.synthesis(text2, lang='zh', ctp=1, options=options)

        if not isinstance(result, dict):
            with open(file_name, 'wb') as f: # 谭东外网
                a = f.write(result)
                print("a:", a)
            try:
                response = StreamingHttpResponse(open(file_name, 'rb'))
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_name)
                print("response:", response)
                return response

            except Exception as e:
                print("e:", e)
                raise Http404
                # return HttpResponse('{"status": "没有生成音频文件"}')

class SendDataToFrontEndProView(View):
    """专门从后端传递所需数据给前端

    method: Post
    access_url: http://ip:port/senddata
    """
    def post(self, request):
        """处理post请求

        Args:
            NA
        Returns:
            NA
        """
        status = "ok"
        data = [{"data0":"A"}, {"data1":"B"}, {"data2":"C"},]

        return HttpResponse(json.dumps({
            "status": status,
            "data":data,
        }))

        #  可以返回图片
        # return HttpResponse(image, content_type='image/jpg')

class xiaojieView(View):
    """翻译路由
    # TODO: 这个类需要进一步重构
    method: Post
    access_url: http://ip:port/xiaojie
    """
    def post(self, request):
        to_lang = request.POST.get('to_lang') # 全部文本
        input_text = request.POST.get('input_text') # 全部文本
        # status = "ok"
        # data = [{"data0":"A"},{"data1":"B"},{"data2":"C"},]
        #
        # return HttpResponse(json.dumps({
        #         "status": status,
        #         "data":data,
        #     }))

        # to_lang = request.POST.get('to_lang') # 全部文本
        # to_lang = 'zh' # 全部文本
        # input_text = request.POST.get('input_text') # 全部文本
        # input_text = 'apple' # 全部文本
        try:
            output_text = MachineTranslation(to_lang, input_text)
            status = "ok"
        except Exception as e:
            output_text = ''
            status = "failed to translate"
            pass

        data = [{"output_text": output_text}]

        return HttpResponse(json.dumps({
            "status": status,
            "data": data,
        }))

class TranslateView(View):
    """语音翻译机整合逻辑，包括语音识别，翻译和语音合成

    method: Post
    access_url: http://ip:port/translate
    """
    def post(self, request):
        """处理post请求

        Args:
            'language': 输入值zh或en，中文或英文
            'audio_file': 音频文件
        Returns:
            数据处理后结果, 以JSON格式返回, 某一字段返回mp3文件
        """
        print("TranslateView->post method is called.")
        ### 测试视图链接####
        # status = "ok"
        # data = [{"data0":"A"},{"data1":"B"},{"data2":"C"},]
        #
        # return HttpResponse(json.dumps({
        #         "status": status,
        #         "data":data,
        #     }))


        ###判断文件数量，超过一定数量则清空####
        delete_excessive_files(args.file_translate_path, args.files_number)
        # # 判断缓存的文件数量是不是超过一定的值。避免存储空间满了。
        # cache_path= './static/output/audioCache'
        # cache_number= 100
        # delete_excessive_files(cache_path, cache_number)
        ###语音识别部分###
        # language="zh" # 中到英
        # language="en" # 英到中

        audio_file = request.FILES.get('audioFile', None)
        language = request.POST.get('language', None)
        # 将缓存数据合成在本地保存
        # print("Mark1")
        # print("audio_file:", audio_file)
        # print("language:", language)
        if not audio_file or not language or (language != 'zh' and language != 'en'):
            return HttpResponse({"upload audio or language error！"})
        # print("Mark2")
        filecontent = audio_file.read()
        filename = ''.join(audio_file.name) #缓存保存的路径
        # print("cache path", filename)    
        # filename = audio_file.name      
        with open(filename, 'wb') as f:
            f.write(filecontent)
        to_lang = ''
        input_text = ''
        try:
            # 开始语音识别
            res=SpeechRecognition(audio_file, language)
            os.remove(path) # 识别完之后删除缓存文件
            
            # print("返回结果",res)
            # print("返回类型",type(res))
            # 获取状态值
            status=dict_get(res,"status", '')
            # print("返回的status",status)
            # print("返回的status的类型",type(status))
            # 获取错误信息
            message=dict_get(res,"message", '')
            
            try:
                if status =="ok":
                    # print("返回的message",message)
                    # print("返回的message的类型",type(message))
                    # 获取识别出来的数据
                    data=dict_get(res,"data", '')
                    # print("返回的data",data)
                    # print("返回的data的类型",type(data))
                    # 翻译成什么语言
                    to_lang=dict_get(data,"to_lang", '')
                    # print("返回的to_lang",to_lang)
                    # print("返回的to_lang的类型",type(to_lang))
                    # 一开始输入的音频文件的语言
                    # from_lang=dict_get(data,"from_lang", '')
                    # print("返回的from_lang",from_lang)
                    # print("返回的from_lang的类型",type(from_lang))
                    #识别出来的文本
                    input_text=dict_get(data,"result", '')
                    # print("返回的input_text",input_text)
                    # print("返回的input_text的类型",type(input_text))
            except Exception as e:
                print(e)
                return HttpResponse({"error message":message})
        except Exception as e:
            print(e)
            return HttpResponse({"error message":"SpeechRecognition error"})
        ####文本翻译部分部分###

        # to_lang, input_text由建龙部分输出
        # to_lang = 'zh'
        # to_lang = 'en'
        # input_text = '苹果'

        print("机器翻译模块输入文字:", input_text)
        text = MachineTranslation(to_lang, input_text)
        print("机器翻译模块输出文字:", text)

        # return HttpResponse({"statues:ok"}) # 测试

        #语音合成部分###

        # text = "你好！这是翻译机测试功能"  # 翻译过后传入的结果
        # speedVal = 5  # 默认
        # tonesVal = 5  # 默认
        # volumeVal = 5  # 默认
        # role = 0  # 默认

        # 若是前端有输入用前端的，没有的话为默认值
        speedVal = request.POST.get('speedVal', 5)
        tonesVal = request.POST.get('tonesVal', 5)
        volumeVal = request.POST.get('volumeVal', 5)
        role = request.POST.get('role', 0)
        # start3 = datetime.now()
        start3=datetime.datetime.now()
        file_url=VoiceSynthesizer(text, speedVal, tonesVal, volumeVal, role,args.file_translate_path)
        print("返回的结果：",file_url)
        print("返回的类型",type(file_url))
        start4=datetime.datetime.now()
        print(start4 - start3)
        if file_url.strip() == '':
           status="the audio file is null"
        else:
           status = "ok"

        data = [{"audioFileUrl":file_url},{"dentifiedText":input_text},{"translatedText":text}]
        return HttpResponse(json.dumps({
                "status": status,
                "data":data,
            }))

class UrunTTSView(View):
    """自研TTS

    method: Post
    access_url: http://ip:port/uruntts
    """

    def post(self,request):
        """处理post请求

        Args:
            'read_text': 准备合成的文本
        Returns:
            通过json类型发送给前端所需的内容,包括生成的mp3文件的url
        """
        pass
        # # 可以根据自己的需要增加字段
        # # read_text_1 = request.POST.get('read_text_1',"欢迎使用云润语音合成技术第一句")
        # # read_text_2 = request.POST.get('read_text_2',"欢迎使用云润语音合成技术第二句")
        #
        # global sentences  # 准备合成的句子的存放列表
        # sentences = []
        # read_text= request.POST.get('read_text',"欢迎使用云润语音合成技术")
        # print("准备读的句子：",read_text)
        # print("准备读的句子的类型：",type(read_text))
        # read_text = text_to_pinyin(read_text)
        # print("转换为拼音的句子：",read_text)
        # print("转换为拼音的句子的类型：",type(read_text))
        # sentences.append(read_text)
        # print(sentences)
        # print(type(sentences))
        # sentences_num=len(sentences) #数据句子的数量
        # # urunTTS(sentences) # 合成句子
        #
        # # 返回合成的mp3文件给前端调用
        # # file_name = '/Users/ccs/Desktop/DjangoDemoTangdong/static/output/urunTTS_output/'
        # file_name = './static/output/urunTTS_output/'
        # nowTime = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')  # 现在
        # save_file = file_name + nowTime + '.wav'
        # print("文本保存",save_file)
        # file_url = "http://" +  + ":" + str(
        #     port) + "/static/output/web_output/" + nowTime + '.mp3'
        # print("file_url", file_url)
        # data = [{"file_url": file_url}, ]
        #
        # # 判断生成的文件是否超过一定的数量
        # ###判断文件数量，超过一定数量则清空####
        # folder_path= './static/output/urunTTS_output/'
        # files_number= 100
        # delete_excessive_files(folder_path, files_number)
        #
        # return HttpResponse(json.dumps({
        #         # "status": status,
        #         "data":data,
        #
        #     }))



class en_qa_View(View):     
    def post(self,request):
	    ### 获取输入，储存输入 ###
        # 从前端获取语言类型和问题。问题的输入形式为语音。
        questionMP3=request.FILES.get('question', None)
        knowledge_source=request.POST.get('knowledge_source', 'en_wikipedia')
        startPoint=time.time()
        # 检查输入是否符合要求
        print(not questionMP3)
        print(knowledge_source)
        if not questionMP3 or (knowledge_source != 'en_wikipedia' and knowledge_source != 'cn_wikipedia'):
            return HttpResponse({"upload audio or knowledge source error！"})
        # 清除缓存，避免储存满
        delete_excessive_files(args.file_translate_path, args.files_number) 
        # 储存输入的问题
        questionCont=questionMP3.read()
        path=''.join(questionMP3.name) 
        with open(path, 'wb') as f:
            f.write(questionCont)
        
        ### 调用语音识别模块和翻译模块将以语音形式输入的问题转化为英语文本 ###
        # 先将语音输入转换文本形式
        try:
            # The start point of the speech recognition of the input question
            # SR_q_s = time.time()
            res=SpeechRecognition(path,'en')
            #res=SpeechRecognition(questionMP3, 'en')
            os.remove(path)
            status=dict_get(res,"status", '')
            # 获取错误信息
            message=dict_get(res,"message", '')

            try:
                if status == 'ok':
                    # print(message)
                    # print (type(message))
                    # 获取识别出来的数据
                    data = dict_get(res, 'data', '')
                    # print (’返回的data‘, data)
                    # print('返回的data类型'， type(data))
                    # 获取 target language， 即要翻译成的语言
                    to_lang = dict_get(res, 'to_lang', '')
                    # print ('翻译成'， to_lang)
                    # print ('to_lang的数据类型'， type(to_lang))
                    # 获取 source language， 即输入的语言
                    from_lang=dict_get(res, 'from_lang', '')
                    # print ('输入语言为'， from_lang)
                    # print('from_lang的数据类型'， type(from_lang))
                    # 识别出来的文本
                    question=dict_get(data, 'result', '')
                    # The end point of the speech recognition of the question
                    # SR_q_e = time.time()
                    # print ('The time spent in speech recognition of the question is: ', SR_q_e-SR_q_s)
                    # print('对输入问题的语音识别结果： ', question)
                    # performanceAnalysis.write (question+ "," + str(SR_q_e-SR_q_s) + ",")
                    # print ('返回的input_text', input_text)
                    # print ('返回的input_text 类型'， type(input_text))
                    
            except Exception as e:
                print (e)
                return HttpResponse({'error message: ', message})
        except Exception as e:
            print (e)
        
        ### QA模块。将问题输入QA系统，输出问题的答案 ### 
        # 先确定问题是事实类还是非事实类问题
        # classifier_start = time.time()
        '''try: 
            label = classifier([question]) 
        # classifier_end = time.time()
            print ('The category that the question belongs to is: ', label)
        # print ('The time spent in a classifier is: ', str(classifier_end-classifier_start))
           except Exception as e:
            print(e)
            print('Failed to classify!')
        if label == 0:
            return HttpResponse({"The input question is not a factoid question. Please input a factoid one!"})
        '''
        try:
                if question[-1]!='?':
                    question+='?'
                question = question.capitalize()
                print ('The input question of DrQA is: ', question)
                # The start point of qa
                # QA_s = time.time()
                # print ('The input question is: ', question)
                answer= fbqa(question, knowledge_source)
                # The end point of qa
                # QA_e = time.time()
                # print ('The time spent in QA is: ', QA_e-QA_s)
                print('The answer is: ', answer)
                # performanceAnalysis.write(answer+","+str(QA_e-QA_s)+",")
                if answer.isdigit():
                    answer = 'It is '+answer
        except Exception as e:
                        print(e)
                        print('Failed to answer the question.')
        
        ### 输出模块 ###
        # 输出答案的语音和文本两种形式
        # 从前端获取或者默认设置语音合成的参数
        # The start point of voice synthesis of the answer
        # VS_a_s = time.time()
        speedVal=request.POST.get('SpeedVal', 5)
        tonesVal=request.POST.get('TonesVal', 5)
        volumeVal=request.POST.get('VolumeVal',5)
        role=request.POST.get('role', 5)

        try:
            file_url=VoiceSynthesizer(answer, speedVal, tonesVal, volumeVal, role, args.file_translate_path)
        except Exception as e:
            print (e)
            print ('Failed in voice synthesis!')
            file_url = ''
        if file_url == '':
            print('The output file does not exist.')
        endPoint = time.time()
        print ('The process time is:', endPoint-startPoint)
        # print ('The time spent in voice synthesis of the answer is: ', endPoint-VS_a_s)
        # performanceAnalysis.write(file_url+","+str(endPoint-VS_a_s)+"\n")
        # 向前端输出最终结果，包括答案的语音文件所在的url和答案的文本形式
        answer_path = file_url.replace('/app/QA_DATA/', '')
        final_answer_path = 'https://ai.urundata.com.cn:38001/'+ answer_path
        return HttpResponse(json.dumps({"status":'ok', "questionText":question, "answerText":answer, "file_url":final_answer_path,}))


class cn_qa_View(View):
    ### 利用语义匹配回答问题 ###     
    def post(self,request):
	    ### 获取输入，储存输入 ###
        # performanceAnalysis = open("performance.csv", "a+")
        # performanceAnalysis.write('SRofQ_result,SRofQ_time,MTofQ_result,MTofQ_time,QA_result,QA_time,MTofA_result,MTofA_time,VSofA_result,VSofA_time\n')
        # 从前端获取语言类型和问题。问题的输入形式为语音。
        questionMP3=request.FILES.get('question', None)
        knowledge_source = request.POST.get('knowledge_source', 'en_wikipedia')
        startPoint=time.time()
        # 检查输入是否符合要求
        if not questionMP3 or (knowledge_source != 'en_wikipedia' and knowledge_source != 'cn_wikipedia'):
            return HttpResponse({"upload audio or knowledge source error！"})
        # 清除缓存，避免储存满
        delete_excessive_files(args.file_translate_path, args.files_number) 
        # 储存输入的问题
        questionCont=questionMP3.read()
        path=''.join(questionMP3.name) 
        with open(path, 'wb') as f:
            f.write(questionCont)
        
        ### 调用语音识别模块将以语音形式输入的问题转化为文本 ###
        # 先将语音输入转换文本形式
        try:
            # The start point of the speech recognition of the input question
            # SR_q_s = time.time()
            res=SpeechRecognition(questionMP3,'zh')
            os.remove(path)

            status=dict_get(res,"status", '')
            # print("返回的status",status)
            # print("返回的status的类型",type(status))
            # 获取错误信息
            message=dict_get(res,"message", '')

            try:
                if status == 'ok':
                    # print(message)
                    # print (type(message))
                    # 获取识别出来的数据
                    data = dict_get(res, 'data', '')
                    # print (’返回的data‘, data)
                    # print('返回的data类型'， type(data))
                    # 获取 target language， 即要翻译成的语言
                    to_lang = dict_get(res, 'to_lang', '')
                    # print ('翻译成'， to_lang)
                    # print ('to_lang的数据类型'， type(to_lang))
                    # 获取 source language， 即输入的语言
                    from_lang=dict_get(res, 'from_lang', '')
                    # print ('输入语言为'， from_lang)
                    # print('from_lang的数据类型'， type(from_lang))
                    # 识别出来的文本
                    ch_question=dict_get(data, 'result', '')
                    # The end point of the speech recognition of the question
                    # SR_q_e = time.time()
                    # print ('The time spent in speech recognition of the question is: ', SR_q_e-SR_q_s)
                    print('对输入问题的语音识别结果： ', ch_question)
                    # performanceAnalysis.write (question+ "," + str(SR_q_e-SR_q_s) + ",")
                    # print ('返回的input_text', input_text)
                    # print ('返回的input_text 类型'， type(input_text))
                    
            except Exception as e:
                print ('Speech Recognition is not OK!')
                print (e)
                return HttpResponse({'error message: ', message})
        except Exception as e:
            print (e)
            print ('Failed in speech recognition!')
        
        try:
            print ('输入的中文问题：', ch_question)
            # The start point of the machine translation of the question
            # MT_q_s = time.time()
            en_question = MachineTranslation('en', ch_question) 
            # The end point of the machine translation of the question
            # MT_q_e = time.time()
            # print ('The time spent in machine translation of the question is: ', MT_q_e-MT_q_s)
            print ('翻译成英文后的问题：', en_question)
            # performanceAnalysis.write(question+","+str(MT_q_e-MT_q_s)+",")
            status = 'OK'
        except:
            status= 'Failed to translate.'
            HttpResponse({status})
        
        ### QA模块。将问题输入QA系统，输出问题的答案 ### 
        # 先确定问题是事实类还是非事实类问题
        # question_list = ['What is question answering?']
        # classifier_start = time.time()
        if en_question[-1]!='?':
            en_question+='?'
            # print(question)
        try:
            label = classifier([en_question]) 
            print ('问题类别是： ', label)
        except Exception as e:
            print (e)
            print ('Fail to classify!')
        # classifier_end = time.time()
        # print ('The time spent in a classifier is: ', str(classifier_end-classifier_start))
    
        if label == 0:
            return HttpResponse(json.dumps({"status":'not ok', "questionText":ch_question,}))
        
        try:
            similar_question, answers, score = semantics_matching(ch_question)
            print ('与输入问题最相似的问题是： ', similar_question)
            print ('快速匹配的答案是： ', answers[0])
            print ('快速匹配获得的答案的分数： ', score)
            answer = answers[0]
        except Exception as e:
            print(e)
            print('Failed to answer the question.')
        if score < 0.8 or answer == '':
            try:
                en_question = en_question.capitalize()
                if en_question[-1]!='?':
                    en_question+='?'
                    print(question)
                answer= fbqa(en_question, knowledge_source)
                print ('输出的答案是: ', answer)
            except Exception as e:
                print (e)
                print ('Fail to answer the question!')
            # The end point of qa
            # QA_e = time.time()
            # print ('The time spent in QA is: ', QA_e-QA_s)
            # print('得到的答案：', answer)
            # performanceAnalysis.write(answer+","+str(QA_e-QA_s)+",")

            # 如果输入的是中文问题，则输出中文答案；如果是英文问题，则输出英文答案。
            # 答案包括文本和语音两种形式。
            # 如果要求的语言类型是中文，那么先要将英文的答案翻译成中文
            try:
                # The start point of the machine translation of the answer
                # MT_a_s = time.time()
                answer = MachineTranslation('zh', answer)
                # The end point of the machine translation of the answer
                # MT_a_e = time.time()
                # print ('The time spent in machine translation of the answer is: ', MT_a_e-MT_a_s)
                print ('最终得到的中文答案： ', answer)
                # performanceAnalysis.write(answer+","+str(MT_a_e-MT_a_s)+",")
            except Exception as e:
                print(e)
                print('Failed to translate the English answer into Chinese.')

        ### 输出模块 ###
        # 当答案已经为所要求的语言类型时，输出答案的语音和文本两种形式
        # 从前端获取或者默认设置语音合成的参数
        # The start point of voice synthesis of the answer
        # VS_a_s = time.time()
        speedVal=request.POST.get('SpeedVal', 5)
        tonesVal=request.POST.get('TonesVal', 5)
        volumeVal=request.POST.get('VolumeVal',5)
        role=request.POST.get('role', 5)

        try:
            file_url=VoiceSynthesizer(answer, speedVal, tonesVal, volumeVal, role, args.file_translate_path)
        except Exception as e:
            print (e)
            print ('Failed in voice synthesis!')
            file_url = ''
        if file_url == '':
            print('The output file does not exist.')
        endPoint = time.time()
        print ('The process time is:', endPoint-startPoint)
        # print ('The time spent in voice synthesis of the answer is: ', endPoint-VS_a_s)
        # performanceAnalysis.write(file_url+","+str(endPoint-VS_a_s)+"\n")
        # 向前端输出最终结果，包括答案的语音文件所在的url和答案的文本形式
        answer_path = file_url.replace('/app/QA_DATA/', '')
        final_answer_path = 'https://ai.urundata.com.cn:38001/'+ answer_path
        return HttpResponse(json.dumps({"status":"ok", "questionText":ch_question, "answerText":answer, "file_url":final_answer_path,}))

class cn_qa_View1(View):
        ### 利用语义匹配回答问题 ###     
    def post(self,request):
	    ### 获取输入，储存输入 ###
        # performanceAnalysis = open("performance.csv", "a+")
        # performanceAnalysis.write('SRofQ_result,SRofQ_time,MTofQ_result,MTofQ_time,QA_result,QA_time,MTofA_result,MTofA_time,VSofA_result,VSofA_time\n')
        # 从前端获取语言类型和问题。问题的输入形式为语音。
        questionMP3=request.FILES.get('question', None)
        knowledge_source = request.POST.get('knowledge_source', 'en_wikipedia')
        startPoint=time.time()
        # 检查输入是否符合要求
        if not questionMP3 or (knowledge_source != 'en_wikipedia' and knowledge_source != 'cn_wikipedia'):
            return HttpResponse({"upload audio or knowledge source error！"})
        # 清除缓存，避免储存满
        delete_excessive_files(args.file_translate_path, args.files_number) 
        # 储存输入的问题
        questionCont=questionMP3.read()
        path=''.join(questionMP3.name)
        if len(path.split('.')[-1])==4:
            path=path[:-1]
        #print(98,path)        
        with open(path, 'wb') as f:
            f.write(questionCont)
        
        ### 调用语音识别模块将以语音形式输入的问题转化为文本 ###
        # 先将语音输入转换文本形式
        try:
            # The start point of the speech recognition of the input question
            # SR_q_s = time.time()
            #res=SpeechRecognition(questionMP3,'zh')
            res=SpeechRecognition(path,'zh') 
            os.remove(path)

            status=dict_get(res,"status", '')
            # print("返回的status",status)
            # print("返回的status的类型",type(status))
            # 获取错误信息
            message=dict_get(res,"message", '')

            try:
                if status == 'ok':
                    # print(message)
                    # print (type(message))
                    # 获取识别出来的数据
                    data = dict_get(res, 'data', '')
                    # print (’返回的data‘, data)
                    # print('返回的data类型'， type(data))
                    # 获取 target language， 即要翻译成的语言
                    to_lang = dict_get(res, 'to_lang', '')
                    # print ('翻译成'， to_lang)
                    # print ('to_lang的数据类型'， type(to_lang))
                    # 获取 source language， 即输入的语言
                    from_lang=dict_get(res, 'from_lang', '')
                    # print ('输入语言为'， from_lang)
                    # print('from_lang的数据类型'， type(from_lang))
                    # 识别出来的文本
                    ch_question=dict_get(data, 'result', '')
                    # The end point of the speech recognition of the question
                    # SR_q_e = time.time()
                    # print ('The time spent in speech recognition of the question is: ', SR_q_e-SR_q_s)
                    print('对输入问题的语音识别结果： ', ch_question)
                    # performanceAnalysis.write (question+ "," + str(SR_q_e-SR_q_s) + ",")
                    # print ('返回的input_text', input_text)
                    # print ('返回的input_text 类型'， type(input_text))
                    
            except Exception as e:
                print (e)
                return HttpResponse({'error message: ', message})
        except Exception as e:
            print (e)
            print ('Failed in speech recognition!')
        
        '''try:
            print ('输入的中文问题：', ch_question)
            # The start point of the machine translation of the question
            # MT_q_s = time.time()
            en_question = MachineTranslation('en', ch_question) 
            # The end point of the machine translation of the question
            # MT_q_e = time.time()
            # print ('The time spent in machine translation of the question is: ', MT_q_e-MT_q_s)
            print ('翻译成英文后的问题：', en_question)
            # performanceAnalysis.write(question+","+str(MT_q_e-MT_q_s)+",")
            status = 'OK'
        except:
            status= 'Failed to translate.'
            HttpResponse({status})
        
        ### QA模块。将问题输入QA系统，输出问题的答案 ### 
        # 先确定问题是事实类还是非事实类问题
        # question_list = ['What is question answering?']
        # classifier_start = time.time()
        if en_question[-1]!='?':
            en_question+='?'
            # print(question)
        try:
            label = classifier([en_question]) 
            print ('问题类别是： ', label)
        except Exception as e:
            print (e)
            print ('Fail to classify!')
        # classifier_end = time.time()
        # print ('The time spent in a classifier is: ', str(classifier_end-classifier_start))
    
        if label == 0:
                return HttpResponse(json.dumps({"status":'not ok', "questionText":ch_question,}))
        '''
        try:
            similar_question, answers, score = semantics_matching(ch_question)
            print ('与输入问题最相似的问题是： ', similar_question)
            print ('快速匹配的答案是： ', answers[0])
            print ('快速匹配获得的答案的分数： ', score)
            answer = answers[0]
        except Exception as e:
            print(e)
            print('Failed to answer the question.')
            
        ### 输出模块 ###
        # 当答案已经为所要求的语言类型时，输出答案的语音和文本两种形式
        # 从前端获取或者默认设置语音合成的参数
        # The start point of voice synthesis of the answer
        # VS_a_s = time.time()
        speedVal=request.POST.get('SpeedVal', 5)
        tonesVal=request.POST.get('TonesVal', 5)
        volumeVal=request.POST.get('VolumeVal',5)
        role=request.POST.get('role', 5)

        try:
            file_url=VoiceSynthesizer(answer, speedVal, tonesVal, volumeVal, role, args.file_translate_path)
        except Exception as e:
            print (e)
            print ('Failed in voice synthesis!')
            file_url = ''
        if file_url == '':
            print('The output file does not exist.')
        endPoint = time.time()
        print ('The process time is:', endPoint-startPoint)
        # print ('The time spent in voice synthesis of the answer is: ', endPoint-VS_a_s)
        # performanceAnalysis.write(file_url+","+str(endPoint-VS_a_s)+"\n")
        # 向前端输出最终结果，包括答案的语音文件所在的url和答案的文本形式
        answer_path = file_url.replace('/app/QA_DATA/', '')
        final_answer_path = 'https://ai.urundata.com.cn:38001/'+ answer_path
        return HttpResponse(json.dumps({"status":"ok", "questionText":ch_question, "the_most_similar_quesion":similar_question,  "answerText":answer, "file_url":final_answer_path,}))        

class cn_qa_View2(View):
    ### 利用drqa回答问题 ###     
    def post(self,request):
	    ### 获取输入，储存输入 ###
        # performanceAnalysis = open("performance.csv", "a+")
        # performanceAnalysis.write('SRofQ_result,SRofQ_time,MTofQ_result,MTofQ_time,QA_result,QA_time,MTofA_result,MTofA_time,VSofA_result,VSofA_time\n')
        # 从前端获取语言类型和问题。问题的输入形式为语音。
        questionMP3=request.FILES.get('question', None)
        knowledge_source = request.POST.get('knowledge_source', 'en_wikipedia')
        startPoint=time.time()
        # 检查输入是否符合要求
        if not questionMP3 or (knowledge_source != 'en_wikipedia' and knowledge_source != 'cn_wikipedia'):
            return HttpResponse({"upload audio or knowledge source error！"})
        # 清除缓存，避免储存满
        delete_excessive_files(args.file_translate_path, args.files_number) 
        # 储存输入的问题
        questionCont=questionMP3.read()
        path=''.join(questionMP3.name)
        #print(98,path)
        if len(path.split('.')[-1])==4:
            path=path[:-1]
        #print(99,path)
        with open(path, 'wb') as f:
            f.write(questionCont)
        
        ### 调用语音识别模块将以语音形式输入的问题转化为文本 ###
        # 先将语音输入转换文本形式
        try:
            # The start point of the speech recognition of the input question
            # SR_q_s = time.time()
            res=SpeechRecognition(path,'zh')
            os.remove(path)

            status=dict_get(res,"status", '')
            # print("返回的status",status)
            # print("返回的status的类型",type(status))
            # 获取错误信息
            message=dict_get(res,"message", '')

            try:
                if status == 'ok':
                    # print(message)
                    # print (type(message))
                    # 获取识别出来的数据
                    data = dict_get(res, 'data', '')
                    # print (’返回的data‘, data)
                    # print('返回的data类型'， type(data))
                    # 获取 target language， 即要翻译成的语言
                    to_lang = dict_get(res, 'to_lang', '')
                    # print ('翻译成'， to_lang)
                    # print ('to_lang的数据类型'， type(to_lang))
                    # 获取 source language， 即输入的语言
                    from_lang=dict_get(res, 'from_lang', '')
                    # print ('输入语言为'， from_lang)
                    # print('from_lang的数据类型'， type(from_lang))
                    # 识别出来的文本
                    ch_question=dict_get(data, 'result', '')
                    # The end point of the speech recognition of the question
                    # SR_q_e = time.time()
                    # print ('The time spent in speech recognition of the question is: ', SR_q_e-SR_q_s)
                    print('对输入问题的语音识别结果： ', ch_question)
                    # performanceAnalysis.write (question+ "," + str(SR_q_e-SR_q_s) + ",")
                    # print ('返回的input_text', input_text)
                    # print ('返回的input_text 类型'， type(input_text))
                    
            except Exception as e:
                print (e)
                return HttpResponse({'error message: ', message})
        except Exception as e:
            print (e)
            print ('Failed in speech recognition!')
        
        try:
            print ('输入的中文问题：', ch_question)
            # The start point of the machine translation of the question
            # MT_q_s = time.time()
            en_question = MachineTranslation('en', ch_question) 
            # The end point of the machine translation of the question
            # MT_q_e = time.time()
            # print ('The time spent in machine translation of the question is: ', MT_q_e-MT_q_s)
            print ('翻译成英文后的问题：', en_question)
            # performanceAnalysis.write(question+","+str(MT_q_e-MT_q_s)+",")
            status = 'OK'
        except:
            status= 'Failed to translate.'
            HttpResponse({status})
        '''
        ### QA模块。将问题输入QA系统，输出问题的答案 ### 
        # 先确定问题是事实类还是非事实类问题
        # question_list = ['What is question answering?']
        # classifier_start = time.time()
        try:
            label = classifier([en_question]) 
            print ('问题类别是： ', label)
        except Exception as e:
            print (e)
            print ('Fail to classify!')
        # classifier_end = time.time()
        # print ('The time spent in a classifier is: ', str(classifier_end-classifier_start))
    
        if label == 0:
                return HttpResponse({"请输入一个事实性问题。"})
        '''
        try:
            en_question = en_question.capitalize()
            if en_question[-1]!='?':
                en_question+='?'
            print('The input question of DrQA is:', en_question)
            answer= fbqa(en_question, knowledge_source)
            print ('输出的答案是: ', answer)
        except Exception as e:
            print (e)
            print ('Fail to answer the question!')
            # The end point of qa
            # QA_e = time.time()
            # print ('The time spent in QA is: ', QA_e-QA_s)
            # print('得到的答案：', answer)
            # performanceAnalysis.write(answer+","+str(QA_e-QA_s)+",")

            # 如果输入的是中文问题，则输出中文答案；如果是英文问题，则输出英文答案。
            # 答案包括文本和语音两种形式。
            # 如果要求的语言类型是中文，那么先要将英文的答案翻译成中文
        try:
            # The start point of the machine translation of the answer
            # MT_a_s = time.time()
            answer = MachineTranslation('zh', answer)
            # The end point of the machine translation of the answer
            # MT_a_e = time.time()
            # print ('The time spent in machine translation of the answer is: ', MT_a_e-MT_a_s)
            print ('最终得到的中文答案： ', answer)
            # performanceAnalysis.write(answer+","+str(MT_a_e-MT_a_s)+",")
        except Exception as e:
            print(e)
            print('Failed to translate the English answer into Chinese.')

        ### 输出模块 ###
        # 当答案已经为所要求的语言类型时，输出答案的语音和文本两种形式
        # 从前端获取或者默认设置语音合成的参数
        # The start point of voice synthesis of the answer
        # VS_a_s = time.time()
        speedVal=request.POST.get('SpeedVal', 5)
        tonesVal=request.POST.get('TonesVal', 5)
        volumeVal=request.POST.get('VolumeVal',5)
        role=request.POST.get('role', 5)

        try:
            file_url=VoiceSynthesizer(answer, speedVal, tonesVal, volumeVal, role, args.file_translate_path)
        except Exception as e:
            print (e)
            print ('Failed in voice synthesis!')
            file_url = ''
        if file_url == '':
            print('The output file does not exist.')
        endPoint = time.time()
        print ('The process time is:', endPoint-startPoint)
        # print ('The time spent in voice synthesis of the answer is: ', endPoint-VS_a_s)
        # performanceAnalysis.write(file_url+","+str(endPoint-VS_a_s)+"\n")
        # 向前端输出最终结果，包括答案的语音文件所在的url和答案的文本形式
        answer_path = file_url.replace('/app/QA_DATA/', '')
        final_answer_path = 'https://ai.urundata.com.cn:38001/'+ answer_path
        return HttpResponse(json.dumps({"status":"ok", "questionText":ch_question, "answerText": answer, "file_url":final_answer_path,}))


          

