# -*- coding: utf-8 -*-
"""
Connect screen module template

Copy this module one level up, to gamesrc/conf/, name it what
you want and modify it to your liking.

Then you set settings.CONNECTION_SCREEN_MODULE to point to your
new module.


 This module holds textual connection screen definitions. All global
 string variables (only) in this module are read by Evennia and
 assumed to define a Connection screen.

 The names of the string variables doesn't matter (but names starting
 with an underscore will be ignored), but each should hold a string
 defining a connection screen - as seen when first connecting to the
 game (before having logged in).

 OBS - If there are more than one global string variable in this
 module, a random one is picked!

 After adding new connection screens to this module you must either
 reboot or reload the server to make them available.

"""

# comment this out if wanting to completely remove the default screen
# from src.commands.connection_screen import DEFAULT_SCREEN

## uncomment these for showing the name and version
# from django.conf import settings
# from src.utils import utils

## A copy of the default screen to modify

CUSTOM_SCREEN = \
"""{c=============================================================={n
 欢迎来到Evennia的演示游戏！当前版本的日期为{y2014年12月13日{n。
 {r（由于游戏数据结构发生改变，12月5日前的老用户需要重新注册才能进入游戏，
 对此我深表歉意。）{n

 这是一个很小的适合单人游玩的游戏，游戏情节非常简短，仅用于展示Evennia
 系统的特性。游戏内容源自Evennia的tutorial world。由于会不定期地更改
 游戏代码及数据结构，{r用户的游戏进度、数据可能会部分或全部丢失{n，敬请谅解。
 
 该游戏使用了链接式的操作模式，除了在登录时需要输入用户名和密码外，其余
 时间玩家可以完全通过点击来进行游戏。当然，你依然可以通过键入命令进行游
 戏，但你的客户端需要能输入中文。在游戏中输入{whelp{n可以查看当前可用的命令。
 由于使用了链接功能，某些Mud客户端可能无法支持该游戏，如TinTin++，建
 议使用网页客户端或MUSHClient。在Windows中建议选择GBK模式。
 
 Evennia是一款开源的MUD类游戏的服务器软件，它基于Python开发，使用BSD
 许可协议发布，对商业应用友好。想了解更多信息欢迎访问 {wEvennia中文站{n
 http://www.evenniacn.com 。
 
 游戏攻略提示：
 古树远眺现蹊径  神器方能斩幽灵
 老根背后乾坤广  方尖碑上指迷津
{c=============================================================={n"""
# % (settings.SERVERNAME, utils.get_evennia_version())

## Minimal header for use with contrib/menu_login.py

# MENU_SCREEN = \
# """{b=============================================================={n
#  Welcome to {g%s{n, version %s!
# {b=============================================================={n""" \
# % (settings.SERVERNAME, utils.get_evennia_version())
