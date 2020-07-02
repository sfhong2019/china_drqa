# /usr/bin/env python
# coding=utf-8

import sys
import base64
import http.client
import hashlib
import urllib.request
import random
import json
import time
import pyaudio    # 捕获语音
import os
import datetime
import subprocess
import socket
from pprint import pprint
from aip import AipSpeech
from datetime import datetime
from config import args

# 语音识别与合成的客户端client
client = AipSpeech(args.APP_ID, args.API_KEY, args.SECRET_KEY)
# aip = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 百度翻译服务的认证信息，注意目前翻译服务并无使用client
appid = args.APP_ID2
secretKey = args.SECRET_KEY2

def MachineTranslation(to_lang: str='zh', input: str='apple') -> str:
    """机器翻译

    Args:
        to_lang: str='zh' 目标翻译语言
        input: str='apple' 输入到翻译模块的文字
    Returns:
        翻译结果，以JSON格式返回
    """
    print("MachineTranslation(...) begins...")
    ret = ''
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

    http_client = None
    salt = random.randint(32768, 65536)
    sign = appid + input + str(salt) + secretKey
    m1 = hashlib.new('md5')
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    url = url + '?q=' + urllib.request.quote(
        input) + '&from=' + 'auto' + '&to=' + to_lang + '&appid=' + appid + '&salt=' + str(salt) + '&sign=' + sign

    try:
        http_client = http.client.HTTPConnection('api.fanyi.baidu.com')
        http_client.request('GET', url)
        # response是HTTPResponse对象
        response = http_client.getresponse()
        result = response.read()

        data = json.loads(result)
        output = data['trans_result'][0]['dst']
        ret = output
    except Exception as e:
        ret=''
    finally:
        if http_client:
            http_client.close()
    print("MachineTranslation(...) ends.")
    return ret


def VoiceSynthesizer(text, speedVal, tonesVal, volumeVal, role, save_path):
    """语音合成

    Args:
        text: 需要进行语音合成的文字
        speedVal: 语速，取值0-9，默认为5中语速
        tonesVal: 音调，取值0-9，默认为5中语调
        volumeVal: 音量，取值0-15，默认为5中音量
        role: 发音人选择, 0为女声，1为男声， 3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
        save_path: 生成的音频文件保存的路径
    Returns:
        识别结果，以JSON格式返回
    """
    print("VoiceSynthesizer(...) begins...")
    options = {}  # setting
    text = str(text)
    options['spd'] = str(speedVal)    # 语速，取值0-9，默认为5中语速
    options['pit'] = str(tonesVal)    # 音调，取值0-9，默认为5中语调
    options['vol'] = str(volumeVal)   # 音量，取值0-15，默认为5中音量
    options['per'] = str(role)    # 发音人选择, 0为女声，1为男声， 3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
    #  实例化AipSpeech
    result = client.synthesis(text, lang='zh', ctp=1, options=options)
    print ('The type of result:',type(result))

    nowTime = datetime.now().strftime('%YY%mM%dD%Hh%Mm%Ss')  # 现在
    secondStamp =str(time.time()*10000000)
    # save_file = args.file_translate_path + nowTime + secondStamp +'.mp3'
    save_file = save_path + nowTime + secondStamp +'.mp3'
    print("文本保存", save_file)
    save_path_1=save_path.replace('.','')
    print("save_path_1", save_path_1)
    global file_url
    file_url=''
    try:
        if not isinstance(save_file, dict):
            with open(save_file, 'wb') as f:
                f.write(result)
                # file_url = "http://" + args.local_ip + ":" + str(args.port) + "/static/output/translate_output/" + nowTime + secondStamp + '.mp3'
                # file_url = "http://" + args.local_ip + ":" + str(args.port) + save_path_1 + nowTime + secondStamp + '.mp3'
                # file_url = "https://ai.urundata.com.cn:38001/api/translation" +save_path_1 + nowTime + secondStamp + '.mp3'
                file_url = save_path_1 + nowTime + secondStamp + '.mp3'
                print("file_url", file_url)
                print("VoiceSynthesizer(...) ends.")
            return file_url
    except Exception as e:
        print(e)
        file_url=''
        return file_url

def SpeechRecognition(audio_file, language):
    """语音识别

    Args:
        audio_file: 音频文件
        language: 语言
    Returns:
        识别结果，以JSON格式返回
    """
    print("SpeechRecognition(...) begins...")
    # TODO: the purpose of using ffmpeg lib is what?
    format=False
    # 判断中英文
    if language == 'zh':
        num = 1537
        to_lang = 'en'
        from_lang = 'zh'
    else:
        num = 1737
        to_lang = 'zh'
        from_lang = 'en'
    # file_content= audio_file.read()
    #filename = ''.join(audio_file.name)
    filename=''.join(audio_file)    
    if len(filename.split('.')[-1])==4:
        filename=filename[:-1]
    print(99,[filename])
    if filename[-3:]!="wav":
        format=True
        filename = filename[:-4] + '.wav'
        command = 'ffmpeg -y -i %s -ar 16000 %s' % (audio_file, filename)
        subprocess.call(command, shell=True)
        print("经ffmpeg转换后文件名：", filename)
    with open(filename, 'rb') as f:
        file_content = f.read()
    data = client.asr(file_content, 'wav', 16000, {
        'dev_pid': num,
    })
    if format:
        os.remove(filename)
    print("data",data)
    message = "successful"
    status = "error"
    result = ""
    if "err_no" in data:
        if data['err_no'] == 0:
            status = "ok"
            result = data['result'][0]
        else :
            message = "the audio quality is poor" #音频质量差
    else :
        message = "network connection timeout" # 网络连接超时

    esponse_data = {"to_lang": to_lang, "from_lang": from_lang, "result": result}
    res = {"status": status, "message": message, "data": esponse_data}
    print("SpeechRecognition(...) ends.")
    return res

if __name__ == '__main__':
    pass
    # 测试语音合成
    # text = "你好！这是翻译机测试功能"  # 翻译过后传入的结果
    # speedVal = 5  # 默认
    # tonesVal = 5  # 默认
    # volumeVal = 5  # 默认
    # role = 0  # 默认
    # file_url = VoiceSynthesizer(text, speedVal, tonesVal, volumeVal, role)

    # 测试语音识别
    # audio_file = "/Users/ccs/Desktop/DjangoDemoTangdong/static/output/translate_output/2019-06-13_14h40m32s.mp3"
    # language = "zh"
    # res = SpeechRecognition(audio_file,language)
    # print("result",res)
    # print("result",type(res))
    # nowTime = datetime.now().strftime('%YY%mM%dD%Hh%Mm%Ss')  # 现在
    # print(nowTime)
