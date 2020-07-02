# 中英文语音翻译机接口文档 

### 1. 接口功能
将客户端上传的中/英语音，经过翻译后，合成翻译目标语言的语音文件返回。

### 2. 接口详情
#### 2.1 访问 
访问| - 
---|---
地址 | https://ai.urundata.com.cn:38001/api/translation/translate (TODO: 貌似已经失效？)
请求方式 | POST

#### 2.2 参数 
| 参数| 必填| 类型| 说明 |
| ---|---|---|---|
|language | 是 | string | 输入语音为中文则为‘zh’,英文则为‘en’ |
|audioFile | 是 | file | 准备翻译的音频文件。格式为.mp3或者.wav|
|speedVal | 否 | string | 语速，取值0-15。默认为5中语速|
|tonesVal | 否 | string | 音调，取值0-15。默认为5中语速|
|volumeVal | 否 | string | 音量，取值0-15。默认为5中语速|
|role | 否 | string | 发音人选择, 0为普通女声，1为普通男生，3为情感合成-逍遥（武侠），4为情感合成-萌妹.默认为普通女声 |

#### 2.3 文件
|参数| 文件类型| MIME类型| 说明|
|---|---|---|---|
|audioFileUrl| *.mp3 | audio/mpeg| 翻译后合成的拼音文件|

#### 2.4 访问状态 
|结果| status |
|---|---|
调用成功| status = "ok"| 
调用失败| status="the audio file is null"| 

### 3. 示例 
#### 3.1 成功 
英-中

    {
        "status": "ok",
        "data": [
            {
             "audioFileUrl": "音频文件的链接"
            }，
            {
            "dentifiedText": "识别出来（翻译前）的文本"
            },
            {
            "translatedText": "翻译过后（准备合成）的文本"
            }.
            
        ]
    }
    
中 - 英

    {
        "status": "ok",
        "data": [
            {
             "audioFileUrl": "音频文件的链接"
            }，
            {
            "dentifiedText": "识别出来（翻译前）的文本"
            },
            {
            "translatedText": "翻译过后（准备合成）的文本"
            }.
            
        ]
    }

#### 3.2 失败 
##### 3.2.1 若是无音频文件输入

    {
       “upload audio or language error！”
    }
##### 3.2.2 若是有音频文件输入，但是无声音

    {
       "status": "the audio file is null",
       "data": [
            {
             "audioFileUrl": ""
            }，
            {
            "dentifiedText": ""
            },
            {
            "translatedText": ""
            }，  
        ]

    }