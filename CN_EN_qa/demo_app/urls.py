from django.conf.urls import url

from . import views

# urlpatterns是被django自动识别的路由列表变量
urlpatterns = [
    # 每个路由信息都需要使用url函数来构造
    # url(路径, 视图)
    url(r'^web$', views.WebView.as_view()), # web后端链接
    url(r'^minipro$', views.MiniProView.as_view()), # 小程序后端链接
    url(r'^senddata$', views.SendDataToFrontEndProView.as_view()), # 从后端传递所需数据给前端
    url(r'^translate$', views.TranslateView.as_view()), # 从后端传递所需数据给前端
    url(r'^xiaojie$', views.xiaojieView.as_view()), # 晓杰的路由
    url(r'^uruntts$', views.UrunTTSView.as_view()), # 云润TTS的路由
    url(r'^en_qa$', views.en_qa_View.as_view()), # 英文问答系统的view
    url(r'^cn_qa$', views.cn_qa_View.as_view()), # 中文问答系统的view
    url(r'^cn_qa_sim_mat$', views.cn_qa_View1.as_view()), # 中文语义匹配问答系统的view    
    url(r'^cn_qa_drqa$', views.cn_qa_View2.as_view()), # 中文drqa问答系统的view
] 
