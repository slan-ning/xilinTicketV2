xilinTicket python 版本
=============

a rapid buy ticket tool for 12306.cn

## 更新日志
* 12-18 19：35 绕过掉线检测
* 12-18 12：53 复活，但是很多非法。。。
* 12-18 11：31 已不能用
* 12-18 10：00 已能用
* 12-18 9：46 他大爷的，昨天修到快23点才修好现在不能用了。。。。
* 12-17 22：40 最新修复版已可用

## 说明
因为c++版本较难维护，又折腾了个python qt的版本，不过用起来很麻烦。

自己使用，随便折腾，不想负责，随时停更，所以没做exe打包，只提供源码。



## 如何使用

1. 安装python3.4

  下载地址：https://www.python.org/ftp/python/3.4.2/python-3.4.2.msi

  安装时，一路next，这个要勾上

  ![环境变量](http://note.youdao.com/yws/public/resource/a89d3315f05760e6d535e841a609e63f/92F8FFC02DDA46E3B1A7D2E2D6A5C54A)



2. 安装pyqt5

  下载地址：http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.3.2/PyQt5-5.3.2-gpl-Py3.4-Qt5.3.1-x32.exe
  
  一路next
  

3. 安装requests
  ```
  开始-》运行-》cmd
  pip install requests
  ```

4. 下载本项目zip包
  点击安装包中的start.bat

##注意事项：
* 刷新间隔不要小于3秒
* 软件在12306卡死的时候，不稳定，所以最好开2个帐号同时刷，挂了一个马上操作另外一个
* 整点没抢到票，一直挂着依然有可能刷到票。（我能说我每次都是捡漏才回家的么）
* 如果失败请退出，重新登录下帐号

##关于添加联系人：
一定得保证要买票的人，在你的12306.cn帐号中存在

1. 先到12306官网添加要加的人
2. 再到软件添加，原谅我很懒，就自己用，懒得做联系人同步功能
