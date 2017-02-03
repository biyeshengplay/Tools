#! /usr/bin/python
# coding=utf-8
import os, re
import shutil
import sys, getopt

def readChannelfile(filename):
    print '-------------- channels start -----------------'
    f = file(filename)
    while True:
        line = f.readline().strip('\n')
        if len(line) == 0:
            break
        else:
            if line[0] == '#' or line[0] == '*':
                continue
            tmp = line.split('=')
            channelsDict[tmp[0]] = tmp[1]
            print '%s : %s'% (tmp[0], tmp[1])
    f.close()
    print '-------------- channels end -----------------'

def getVersionName():
    cmdExtract = r'aapt d badging %s | grep versionName=' % (apkName)
    r = os.popen(cmdExtract)
    text = r.read()
    r.close()
    pat = "versionName='(\d|.*)' "
    name = re.findall(pat, text)[0]
    print 'APK versionName is : %s' % (name)
    return name

def walleAddChannel(channelId, versionName):
    os.makedirs("%s/%s" % (output_channels_apk_dir, channelsDict[channelId]))
    addchannel = r'java -jar walle-cli-all.jar put -c %s %s %s/%s/%s_%s_%s.apk' % (channelId, apkName, output_channels_apk_dir, channelsDict[channelId], easyName, versionName, channelId)
    os.system(addchannel)

def listAllApks(directory):
    num = 0
    for root,dirs,files in os.walk(directory):
        for f in files:
            num += 1
            ff = os.path.abspath(os.path.join(root,f))
            print ff
            os.system('cp %s %s'%(ff, output_all_apk_dir))
    print 'Auto signed %s APKs'% (num)

def listDownloadLink(directory):
    print 'Downloadlink:'
    downloadlinkhead = getDownloadlinkhead(channelsFile)
    for root,dirs,files in os.walk(directory):
        for f in files:
            tmp = os.path.abspath(os.path.join(root,f)).split('/')
            print tmp[len(tmp) - 2].strip('\n').strip('\t').strip('\r') + ' : ' + downloadlinkhead + tmp[len(tmp) - 1]

def getDownloadlinkhead(filename):
    downloadlink = ''
    f = file(filename)
    while True:
        line = f.readline().strip('\n')
        if len(line) == 0:
            break
        else:
            if line[0] == '*':
                downloadlink = line[1:]
    f.close()
    return downloadlink


def extract(package):
    if os.path.exists(package):
        cmdExtract = r'java -jar apktool.jar d -f -s %s -o extract'% (package)
        os.system(cmdExtract)
        srcextract('classes')
        srcextract('classes2')
    else:
        print 'Can not found %s'% (package)

def srcextract(filename):
    if os.path.exists('extract/%s.dex'%(filename)):
        cmdExtract = r'dex2jar/d2j-dex2jar.sh extract/%s.dex -o extract/%s.jar'% (filename, filename)
        os.system(cmdExtract)
    else:
        print 'Can not found extract/%s.dex'% (filename)

def clean():
    print 'cleaning %s...'%(output_apk_dir)
    if os.path.exists(output_apk_dir):
        shutil.rmtree(output_apk_dir)
    print 'cleaning %s...'%('./extract')
    if os.path.exists('./extract'):
        shutil.rmtree('./extract')
    print 'cleaning others...'
    if os.path.exists('./WallePackage.py.bak'):
        os.remove('./WallePackage.py.bak')
    if os.path.exists('./channels.txt.bak'):
        os.remove('./channels.txt.bak')

def distclean():
    clean()
    print 'cleaning apk file...'
    if os.path.exists('./%s'%(apkName)):
        os.remove('./%s'%(apkName))

def usage():
    print 'Auto package & signature APK with different channel ID.'
    print 'Usage:'
    print '  -h   Show help information'
    print '  -p   Auto package & signature'
    print '  -c   Clean work directory, would not delete source APK'
    print '  -d   Distclean work directory, will delete source APK'
    print '  -e package  Extract package to ./extract'

def package():
    if not os.path.exists('./%s'%(apkName)):
        print 'Can not found ./%s!!!\n'%(apkName)
        return

    if os.path.exists(output_apk_dir):
        shutil.rmtree(output_apk_dir)

    os.makedirs(output_channels_apk_dir)
    os.makedirs(output_all_apk_dir)

    readChannelfile(channelsFile)

    versionName = getVersionName()

    for channelId in channelsDict:
        walleAddChannel(channelId, versionName)

    listAllApks(output_channels_apk_dir)
    listDownloadLink(output_channels_apk_dir)
    print '-------------------- Done --------------------'


channelsDict = {}
apkName = 'demo.apk'
easyName = apkName.split('.apk')[0]
channelsFile='channels.txt'
output_apk_dir=os.path.abspath("./out")
output_channels_apk_dir='%s/channels'%(output_apk_dir)
output_all_apk_dir='%s/all'%(output_apk_dir)


print sys.argv
try:
    opts, args = getopt.getopt(sys.argv[1:], "hdpce:")
except getopt.GetoptError,x:
    print 'GetoptError:',x
    usage()
    exit(0)

if len(opts) == 0:
    print 'opts error!'
    usage()
    exit(0)

if len(args) != 0:
    print 'Args error'
    usage()
    exit(0)

for op, value in opts:
    if op == '-c':
        clean()
    elif op == '-d':
        distclean()
    elif op == '-p':
        package()
    elif op == '-e':
        extract(sys.argv[2])
    else:
        usage()
exit(0)
