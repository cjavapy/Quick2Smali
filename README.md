# Quick2Smali
一行代码把apk、jar、dex转成smali，并且用vscode打开。方便快速搜代码。
# 功能:
- 一行命令，反编译apk/jar/dex为smali，并用vscode打开。支持根据时间戳缓存文件，第二次秒开。
- eg: 2s demo-release.apk
# 准备工作：
- 保证py可用
- 安装vscode，并按下面配置code命令
  - 打开vscode，command + shift + p 打开命令面板（或者点击菜单栏 查看>命令面板）
  - 输入shell（选择"install code command in PATH"）
- 配置outputRoot目录。反编译好的smali都会放到该目录下
- 配置bakSmaliJar。用于dex2Smali。没有的下载一个，放在电脑任意目录
- 保证dx命令可用。具体百度
- 把该文件放到任意目录，配置一个别名，比如我配了2s(to Smali的简写)。只需要在控制台输入 2s xxx.apk/dex/jar即可反编译apk、dex、jar，并用vs打开
- mac配置别名方式：
  - 打开终端， open ~/.bash_profile。
  - 配置alias 2s='/Users/xuekai/project/tools/Quick2Smali.py'
  - 保存，打开控制台，输入2s 回车。测试
# TODO:
- 并行处理apk的多dex？(python如何处理多线程)
