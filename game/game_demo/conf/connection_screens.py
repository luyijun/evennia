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
 欢迎来到Evennia的演示游戏！
 
 这是一个非常小的单人游戏，仅用于展示Evennia系统的特性。游戏内容源自
 Evennia的tutorial world，目前游戏还没有全部翻译、改编好。由于游戏
 代码仍在修改，用户的游戏进度、数据可能会全部或部分丢失，敬请谅解。
 
 Evennia是一款开源的MUD类游戏的服务器软件，它基于Python开发，使用BSD
 许可协议发布，对商业应用友好。想了解更多信息欢迎访问 {wEvennia中文站{n
 http://www.evenniacn.com 。
{c=============================================================={n"""
# % (settings.SERVERNAME, utils.get_evennia_version())

## Minimal header for use with contrib/menu_login.py

# MENU_SCREEN = \
# """{b=============================================================={n
#  Welcome to {g%s{n, version %s!
# {b=============================================================={n""" \
# % (settings.SERVERNAME, utils.get_evennia_version())
