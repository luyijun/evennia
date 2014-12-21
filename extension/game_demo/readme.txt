一  简介
该游戏的内容源自Evennia的tutorial world，基本内容都已翻译成中文了。

该游戏使用了链接式的操作模式，除了在登录时需要输入用户名和密码外，其余
时间玩家可以完全通过点击来进行游戏。当然，你依然可以通过键入命令进行游
戏，但你的客户端需要能输入中文。由于使用了链接功能，某些Mud客户端可能
无法支持该游戏，如TinTin++，建议使用网页客户端或MUSHClient。在Windows
中建议选择GBK模式。


二  安装游戏
首先要安装好evennia运行所需的环境（Python、Django、Twisted和GIT），可参见准备开始中的“安装必备软件”部分。

（一）全新安装
如果你想在一个全新的目录中安装游戏，可以按以下步骤操作：

1.  获取游戏源码
2.  进入 evennia/game/ 目录
3.  执行 python manage.py
4.  将 evennia/extension/game_demo/settings.py 中的内容添加到 evennia/game/settings.py 中
    其中的 WEBSOCKET_CLIENT_URL 需要按实际的ip地址调整
5.  执行 python manage.py migrate
6.  执行 python manage.py dbshell 启动数据库交互环境
7.  执行
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_type_list.dat data_object_type_list
    .import data_portable_object_types.dat data_portable_object_types
    将文件中的数据导入数据库
    （如果没有以上的表，请执行 .quit 退出，执行 python manage.py makemigrations，然后再回到第5步）
8.  执行 .quit 退出数据库管理
9.  执行 python evennia.py start 启动游戏
10. 在游戏中以管理员身份执行
    @batchcmd limbo
    @batchcmd build
    创建游戏内容

（二）添加到现有游戏中
如果你已经安装好了evennia，想将游戏添加到现有的环境中，可以按以下步骤操作：

1.  获取游戏源码
2.  将 <游戏源码目录>/extension/game_demo/settings.py 中的内容添加到 <你的游戏目录>/game/settings.py 中
    其中的 WEBSOCKET_CLIENT_URL 需要按实际的ip地址调整
3.  将 <游戏源码目录>/extension/game_demo/ 中的
    data_object_creator_types.dat
    data_object_type_list.dat
    data_portable_object_types.dat 拷贝至 <你的游戏目录>/game/ 中
4.  进入 <你的游戏目录>/game/
5.  执行 python manage.py makemigrations 生成数据迁移文件
6.  执行 python manage.py migrate 生成数据表
7.  执行 python manage.py dbshell 启动数据库交互环境
8.  执行
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_type_list.dat data_object_type_list
    .import data_portable_object_types.dat data_portable_object_types
    将文件中的数据导入数据库
9.  执行 .quit 退出数据库管理
10. 执行 python evennia.py start 启动游戏
11. 在游戏中以管理员身份执行
    @batchcmd limbo
    @batchcmd build
    创建游戏内容


三  相关链接
    游戏演示：http://demo.evenniacn.com/webclient
    游戏网站：http://demo.evenniacn.com


四  更多内容
    如果在安装过程中遇到了问题或想了解更多内容，请访问 http://www.evenniacn.com
