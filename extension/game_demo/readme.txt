一  简介
该游戏的内容源自Evennia的tutorial world，基本内容都已翻译成中文了。

该游戏使用了链接式的操作模式，除了在登录时需要输入用户名和密码外，其余
时间玩家可以完全通过点击来进行游戏。当然，你依然可以通过键入命令进行游
戏，但你的客户端需要能输入中文。由于使用了链接功能，某些Mud客户端可能
无法支持该游戏，如TinTin++，建议使用网页客户端或MUSHClient。在Windows
中建议选择GBK模式。

二  安装
1.  安装evennia最新版
    （请参见 http://www.evenniacn.com/wiki/getting_started.html）
2.  将 extension/game_demo/settings.py 拷贝至 game/ 目录中
    其中的 WEBSOCKET_CLIENT_URL 需要按实际的ip地址调整
3.  将 extension/game_demo/connection_screens.py 拷贝至 game/gamesrc/conf/ 目录中
4.  进入 game/ 目录
    执行 python manage.py makemigrations 创建数据迁移记录
    执行 python manage.py migrate 生成数据表
5.  将 extension/game_demo/ 目录中的
    data_object_creator_types.dat
    data_object_type_list.dat
    data_portable_object_types.dat 拷贝至 game/ 目录中
6.  进入 game/ 目录，执行 python manage.py dbshell
7.  执行
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_creator_types.dat data_object_creator_types
    .import data_object_creator_types.dat data_object_creator_types
    将文件中的数据导入数据库
8.  执行
    .quit
    退出数据库管理
9.  执行 python evennia.py start 启动游戏
10. 在游戏中以管理员身份执行
    @batchcmd limbo
    @batchcmd build
    创建游戏内容

（可选）
11. 可将 extension/other/models.py 拷贝到 src/objects/ 中
    它对物品包含关系进行了缓存，可以显著提高服务端的运行效率，但可靠性尚未经过充分测试。
   
三  更多内容
    如果在安装过程中遇到了问题或想了解更多内容，请访问www.evenniacn.com
