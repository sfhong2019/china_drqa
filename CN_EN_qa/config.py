import socket
import os

class Config:
    """项目配置文件，在这里更改关键项目设置"""

    port = 27703  #准备设置的端口号
    file_translate_path = os.getenv('RESULT_DATA')+'/' # 翻译后生成的音频文件

    file_web_path = './static/output/web_output/' # TTS后生成的音频文件
    myname = socket.getfqdn(socket.gethostname()) # 获取本机电脑名
    local_ip = socket.gethostbyname(myname) # 获取本机ip
    # local_ip = '119.84.122.135' # 棠东服务器ip
    # 第三方预测服务API信息设置
    # TODO：目前使用百度语音识别与语音合成服务，将来需要使用云润自研模型
    APP_ID = '15414045'
    API_KEY = 'BwSTqlxahGvI5k0kGIYDlybZ'
    SECRET_KEY = 'g79fxW3Zqw1qrYKeQHmufv8zNXafc6Vt'
    # TODO：目前使用百度翻译服务，需另外注册一套认证信息
    APP_ID2 = '20190605000305156'
    SECRET_KEY2 = '35gcTMJqQF0stnj3TVTS'
    # domain_name='192.168.9.201:27703',
    domain_name=str(local_ip)+":"+str(port) # 链接域名
    files_number=50  # 判断文件数量超过多少则删除


args = Config  #实体化配置的类

print (args.file_translate_path)

# for DEBUG ONLY
# hostname = socket.gethostname() # 获取本机计算机名称
# ip = socket.gethostbyname(hostname) # 获取本机ip地址
# print(ip)
# port = 27703 # set your port
# file_name={} # Set the path to the file
# print(os.path.realpath(__file__)) # 当前文件的路
