#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import time

# 功能:
#   一行命令，反编译apk/jar/dex为smali，并用vscode打开。支持根据时间戳缓存文件，第二次秒开。
#   eg: 2s demo-release.apk
# 准备工作：
#   0.保证py可用
#   1.安装vscode，并按下面配置code命令
#     1.打开vscode，command + shift + p 打开命令面板（或者点击菜单栏 查看>命令面板）
#     2.输入shell（选择"install code command in PATH"）
#   2.配置outputRoot目录。反编译好的smali都会放到该目录下
#   3.配置bakSmaliJar。用于dex2Smali。没有的下载一个，放在电脑任意目录
#   4.保证dx命令可用。具体百度
#   5.把该文件放到任意目录，配置一个别名，比如我配了2s(to Smali的简写)。只需要在控制台输入 2s xxx.apk/dex/jar即可反编译apk、dex、jar，并用vs打开
#     mac配置别名方式：
#     1.打开终端， open ~/.bash_profile。
#     2.配置alias 2s='/Users/xuekai/project/tools/Quick2Smali.py'
#     3.保存，打开控制台，输入2s 回车。测试
# TODO:
#   1.并行处理apk的多dex？(python如何处理多线程)

outputRoot = "/Users/xuekai/project/Quick2SmaliOutput"
bakSmaliJar = "/Users/xuekai/project/tools/quick2Smali/baksmali.jar"
AXMLPriter2 = "/Users/xuekai/project/tools/quick2Smali/AXMLPrinter2.jar"


def main():
    args = sys.argv[1:]
    file = args[0]
    cache = getCache(file)
    if cache != "":
        openCommand = 'code %s' %cache
        print "有缓冲，直接打开vscode。"+cache
        os.system(openCommand)
        return
    if file.endswith(".apk"):
        result1 = apk2Smali(file)
        result2 =outputManifest(file)
        if result1 and result2:
            openAndSaveCache(file)
    elif file.endswith('.dex'):
        dex2Smali(file)
    elif file.endswith('.jar'):
        jar2Smali(file)
    else:
        print "不支持的类型"
        return


def outputManifest(apkFile):
    # 提取AndroidManifest
    z = zipfile.ZipFile(apkFile,'r')
    z.extract('AndroidManifest.xml', path=getOutPutPath(apkFile), pwd=None)
    z.close()
    command = 'java -jar %s %s/AndroidManifest.xml > %s/AndroidManifest1.xml' %(AXMLPriter2,getOutPutPath(apkFile),getOutPutPath(apkFile))
    if os.system(command) == 0:
        print "解析AndroidManifest成功"
        os.remove(getOutPutPath(apkFile)+"/AndroidManifest.xml")
        os.rename(getOutPutPath(apkFile)+"/AndroidManifest1.xml",getOutPutPath(apkFile)+"/AndroidManifest.xml")
        return True
    else:
        print "解析AndroidManifest成功失败"
        os.remove(getOutPutPath(apkFile)+"/AndroidManifest.xml")
        os.remove(getOutPutPath(apkFile)+"/AndroidManifest1.xml")
        return False



def jar2Smali(jarPath):
    print "准备jar2dex"
    jar2DexCmd ='dx --dex --output=%s %s' %(jarPath+".dex",jarPath)
    if os.system(jar2DexCmd) == 0:
        print "jar2dex成功"
        print "准备dex2Smali"
        command = 'java -jar %s d %s -o %s' %(bakSmaliJar,jarPath+".dex",getOutPutPath(jarPath))
        if os.system(command) == 0:
            print "dex2Smali成功，准备删除临时文件:"+jarPath+".dex"
            os.remove(jarPath+".dex")
        else:
            print "dex2Smali失败，准备删除临时文件:"+jarPath+".dex"
            os.remove(jarPath+".dex")
            return
    else:
        print "jar2Smali失败"
        return
    openAndSaveCache(jarPath)


def dex2Smali(dexPath):
    print "准备dex2Smali"
    command = 'java -jar %s d %s -o %s' %(bakSmaliJar,dexPath,getOutPutPath(dexPath))
    if os.system(command) == 0:
        print "dex2Smali成功"
    else:
        print "dex2Smali失败"
        return
    openAndSaveCache(dexPath)


def apk2Smali(apkPath):
    z =zipfile.ZipFile(apkPath, 'r')
    # apk中的dex列表
    dexList  = []
    for file in z.namelist():
        if (file.endswith(".dex") and file.startswith("classes") and ("/" not in file)):
            dexList.append(file)
    print "准备apk2Smali，apk包含以下dex: "
    print dexList
    for file in dexList:
         dexPath = apkPath+"/"+file
         command = 'java -jar %s d %s -o %s' %(bakSmaliJar,dexPath,getOutPutPath(apkPath))
         print '准备dex2Smali:'+file
         if os.system(command) == 0:
             print "dex2Smali成功"
         else:
             print "dex2Smali失败"
             return False
    return True

# 用vscode打开，并且缓存文件信息
def openAndSaveCache(file):
    openCommand = 'code %s' %getOutPutPath(file)
    os.system(openCommand)
    putCache(file)

# 根据文件名，获取该文件的输出目录
def getOutPutPath(file):
    return outputRoot+"/"+getSimpleOutputFileName(file)

# 获取文件的name（非全路径）
def getSimpleName(file):
    return file.split('/')[-1:][0]

# 获取文件的输出name（非全路径）
def getSimpleOutputFileName(file):
    return file.split('/')[-1:][0]+"_"+time.strftime('%m.%d_%H.%M.%S' , time.localtime(os.path.getctime(file)))

# 传入一个apk/jar/dex等文件名，会把该文件的文件名拼接时间戳，去cache.log中查，如果有，直接返回，否则返回空字符串
def getCache(file):
    simpleName = getSimpleOutputFileName(file)
    try:
        cache = open(outputRoot+"/"+"cache.log",'r')
        for line in cache.readlines():
            if line.replace("\n","")==simpleName:
                outPutFile = getOutPutPath(file)
                if os.path.exists(outPutFile):
                    return getOutPutPath(file)
                else:
                    return ""
    except Exception:
        pass
    return ""

# 写入缓存
def putCache(file):
    simpleName = getSimpleOutputFileName(file)
    cache = open(outputRoot+"/"+"cache.log",'a+')
    print "写入缓存："+simpleName
    cache.write(simpleName+"\n")





#def jar2Smali(jarPath):



if __name__ == '__main__':
    main()
