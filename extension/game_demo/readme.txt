一  简介
该游戏的内容源自Evennia的tutorial world，基本内容都已翻译成中文了。

该游戏使用了链接式的操作模式，除了在登录时需要输入用户名和密码外，其余
时间玩家可以完全通过点击来进行游戏。当然，你依然可以通过键入命令进行游
戏，但你的客户端需要能输入中文。由于使用了链接功能，某些Mud客户端可能
无法支持该游戏，如TinTin++，建议使用网页客户端或MUSHClient。在Windows
中建议选择GBK模式。

二  全新安装
如果你想在一个全新的目录中安装游戏，可以按以下步骤操作：

1.  移动当前目录到你想要安装游戏的地方。
2.  执行
    git clone https://github.com/luyijun/evennia.git 或
    git clone git@github.com:luyijun/evennia.git
3.  执行 python manage.py
4.  将 evennia/extension/game_demo/settings.py 中的内容添加到 evennia/game/settings.py 中
    其中的 WEBSOCKET_CLIENT_URL 需要按实际的ip地址调整
5.  进入 evennia/game/ 目录
6.  执行 python manage.py migrate
7.  执行 python manage.py dbshell 启动数据库交互环境
8.  执行
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_type_list.dat data_object_type_list
    .import data_portable_object_types.dat data_portable_object_types
    将文件中的数据导入数据库
    （如果没有以上的表，请执行 .quit 退出，执行 python manage.py makemigrations，然后再回到第6步）
9.  执行 .quit 退出数据库管理
10. 执行 python evennia.py start 启动游戏
11. 在游戏中以管理员身份执行
    @batchcmd limbo
    @batchcmd build
    创建游戏内容

三  添加到现有游戏中
如果你已经安装好了evennia，想将游戏添加到现有的环境中，可以按以下步骤操作：

1.  将 evennia/extension/game_demo/settings.py 中的内容添加到 evennia/game/settings.py 中
    其中的 WEBSOCKET_CLIENT_URL 需要按实际的ip地址调整
2.  将 evennia/extension/game_demo/connection_screens.py 拷贝至 evennia/game/gamesrc/conf/ 目录中
3.  将 evennia/extension/game_demo/ 目录中的
    data_object_creator_types.dat
    data_object_type_list.dat
    data_portable_object_types.dat 拷贝至 evennia/game/ 目录中
4.  进入 evennia/game/ 目录
    执行 python manage.py makemigrations 生成数据迁移文件
    执行 python manage.py migrate 生成数据表
5.  执行 python manage.py dbshell 启动数据库交互环境
6.  执行
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_type_list.dat data_object_type_list
    .import data_portable_object_types.dat data_portable_object_types
    将文件中的数据导入数据库
7.  执行 .quit 退出数据库管理
8.  执行 python evennia.py start 启动游戏
9.  在游戏中以管理员身份执行
    @batchcmd limbo
    @batchcmd build
    创建游戏内容
   
四  更多内容
    如果在安装过程中遇到了问题或想了解更多内容，请访问www.evenniacn.com
