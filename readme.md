# 项目概述
## 1.背景
采用**YOLOv5s**轻量化目标检测模型，**rtsp**服务器结合**ffmpeg**实现客户端服务器(C/S)之间实时检测视频的推拉流。
## 2.实现过程
### 2.1 采用conda创建虚拟环境，安装所需要的依赖库
`pip install -r requirements.txt`
### 2.2 在main.py修改rtsp地址，加入自己主机的ip地址
- rtmp_server='rtmp://你的ip地址：1935/video'
### 2.3 运行rtsp服务器，再运行main.py,最后采用vlc的网络串口进行拉流
## 3.效果展示
