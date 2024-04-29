#版本 0.011
#date:2023.06.14
import datetime
import time
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon import sync, TelegramClient, events
import json
import socks
import asyncio
import random
import logging
import string
import os
import shutil
from glob import glob
import sys
import platform

#打开广告词文本
with open("ads.txt", "r+", encoding="utf-8") as f:
    text = f.read()
#用等号将广告词分开
sendstr = text.split("========")
#相关的反馈信息
gourpBanStr = "You can't write in this chat (caused by SendMessageRequest)"
gourpBanStr2 = "You can't write in this chat (caused by EditMessageRequest)"
groupBanstr3 = "You're banned from sending messages in supergroups/channels"
groupBanstr4 = "The channel specified is private and you lack permission to access it. Another reason may be that you were banned from it (caused by SendMessageRequest)"
deletedstr = 'The user has been deleted/deactivated'
#打开回复文本
with open("replytext.txt", "r+", encoding="utf-8") as f:
    replytext = f.read()
#用等号将回复文本分开
message = replytext.split("========")

#将文件移动到指定目录,并显示最终移动到了何处
def mymovefile(srcfile, dstpath):  # 移动函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.move(srcfile, dstpath + fname)  # 移动文件
        print("move %s -> %s" % (srcfile, dstpath + fname))

#将session目录下存在的全部tg_session_手机号码提取至config.json中,且api_id和api_hash,也会被提取
def write_to_json():
    #path = os.path.dirname(os.path.realpath('__file__'))
    # print(path)
    session_file = '/session/'
    filePath = path + session_file
    files_list = os.listdir(filePath)
    items = []

    for var in files_list:
        if os.path.splitext(var)[1] == '.session':
            item = {}
            phone = os.path.splitext(var)[0]
            item['phone'] = phone
            item['api_id'] = "6"
            item['api_hash'] = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
            # item.append({'phone':phone,})
            items.append(item)
    accounts = {"accounts": items}
    json.dump(accounts, open(path + "/config.json",
              "w", encoding="utf-8"), indent=4)
    print('导出json文件到主目录')

#导入手机号对应的json文件,并检测json文件的完整性
async def tg_sendmessages(phone, api_id, api_hash):
  #携程池锁
  # async with SEMAPHORE:
    global j
    global running_abnormal_account
    global log

    task = asyncio.current_task()

    try:
        #打开手机号对应的json文件并载入于变量
        with open(path + '/session/' + str(phone) + '.json', 'r', encoding='utf-8') as f:
            phoneJson = json.loads(f.read())

    except:
        print("对应json文件不存在----", phone)
        task.cancel()
        time.sleep(50000)

    try:
        #当参数都存在时直接跳过
        if (phoneJson["device"] and phoneJson["sdk"] and phoneJson["app_version"] and phoneJson["lang_code"] and phoneJson["system_lang_code"]):
            pass

    except:
        print("对应json文件的参数缺失----", phone)
        task.cancel()
        time.sleep(50000)

    # 私信回复开关
    if message_reply == True:
        client = TelegramClient(folder_session + phone, api_id, api_hash, sequential_updates=True, proxy=proxy)
        #client = TelegramClient(folder_session + phone,api_id, api_hash, sequential_updates=True)

        @client.on(events.NewMessage(incoming=True))
        #私信自动回复
        async def handle_new_message(event):
            #print("event", event)
            if event.is_private:  # only auto-reply to private chats

                print('%s--%s--收到一条私人信息:%s' %
                      (time.strftime('%H:%M:%S'), phone, event.message.message))

                # print(time.strftime('%H:%M:%S'), '-', event.message)  # optionally log time and message

                try:
                    await event.respond(message)
                    print('%s--已回复消息' % (phone))
                    await asyncio.sleep(20)
                except Exception as e:
                    print("%s--自动回复消息时出现异常%s" % (phone, e))
                    await asyncio.sleep(20)
    else:

        #客户端连接导入phone_json文件参数
        #不走代理
        client = TelegramClient(folder_session + phone, api_id, api_hash, device_model=phoneJson["device"],
                                system_version=phoneJson["sdk"],
                                app_version=phoneJson["app_version"], lang_code=phoneJson["lang_pack"],
                                system_lang_code=phoneJson["system_lang_pack"])
        #走代理
        # client = TelegramClient(folder_session + phone, api_id, api_hash, device_model=phoneJson["device"], system_version=phoneJson["sdk"],
        #                         app_version=phoneJson["app_version"], lang_code=phoneJson["lang_pack"], system_lang_code=phoneJson["system_lang_pack"],proxy=proxy)
    # 检测连接是否成功
    try:
        time.sleep(1)

        await client.connect()
    except Exception as e:
        print("%s--连接异常：%s" % (phone, e))

    if (await client.is_user_authorized()):

        #sys.stdout = savedStdout
        print('%s--%s--成功登录' % (time.strftime('%H:%M:%S'), phone))
        #sys.stdout = log
    else:
        try:
            await client.disconnect()
        except Exception as e:
            print(phone, '----', e)

        # glob获得路径下所有文件，可根据需要修改.获取指定号码对应的session文件
        src_file_list = glob(src_dir + phone + '.session*')
        for srcfile in src_file_list:
            #当session账号存在问题时,将对应的session文件进行移动
            mymovefile(srcfile, account_banned_dir)  # 移动文件
        task.cancel()
        #sys.stdout = savedStdout
        print("{}--{}--无法正常登录,结束".format(time.strftime('%H:%M:%S'), phone))
        #sys.stdout = log
        await asyncio.sleep(60000)

    chats = []
    # 下面如开启寻找telegram,则开启20s睡眠
    # print("等待获取指定手机号验证码,等待20s")
    # time.sleep(20)
    try:
        #将所有存在的会话进行迭代
        async for dialog in client.iter_dialogs():

            try:

                # if dialog.name == "Telegram":
                #     print('--------------')
                #     print("%s--找到telegram"%(phone))
                #     print("dialog",dialog)
                #     print('--------------')
                #     print("等待60s,再继续执行")
                #     time.sleep(60)
                #如果会话是一个群组,并且会话的username也存在;那么将这个群组会话保存到变量中作为发送对象
                if dialog.entity.megagroup == True and dialog.entity.username:
                    chats.append(dialog)
            except Exception as e:
                #print(phone, "--出现情况:", e)
                pass

    except Exception as e:

        try:
            await client.disconnect()
        except Exception as e:
            print(phone, '----', e)
        #增加异常账号数量
        running_abnormal_account += 1
        task.cancel()
        print("%s--无法正常读取会话框,任务已被结束--运行时异常账号数%s" %
              (phone, running_abnormal_account))
        await asyncio.sleep(60000)

    # #将账号下所拥有的群组名和对应的群组链接导出到export_link.txt
    if write_link == True:
        lll = 0

        ff = open('export_link.txt', 'a+', encoding="utf-8")
        #将账号拥有的群组进行遍历
        for var in chats:

            try:
                #将群组名和对应的群组链接写入export_link.txt,并进行群组可用数量的统计
                full = str(var.entity.username) + '-----' + \
                    str(var.entity.title) + '-----'
                ff.write(full + "\n")
                lll += 1
            except Exception as e:
                print("%s--群链接不存在:%s" % (var.entity.title, e))

        print("%s拥有%s个群,实际可用%s个群" % (phone, len(chats), lll))
        ff.close()

    i = 0
    ii = 0
    # print("chats",len(chats))
    #当发送轮数小于指定轮数时触发条件
    while i < lun:
        banned = 0
        for chat in chats:
            #每次随机选择3个字符
            value = ''.join(random.sample(
                string.ascii_letters + string.digits, 3))
            #每次随机选择要发送的文本序号
            randomstr = random.randint(0, len(sendstr)-1)
            #每次随机要发送的文本信息
            fullSendStr = value + ' ' + sendstr[randomstr]

            try:
                time.sleep(1)
                #将广告词文本发送到群组中
                await client.send_message(entity=chat.entity.id, message=fullSendStr)
                #累计次数
                j += 1
                print("累计%s次--%s--链接:%s--%s" %
                      (j, phone, chat.entity.username, chat.entity.title))

                print("当前时间--%s--间隔:60秒" % (time.strftime('%H:%M:%S')))
                # log.flush()

                time.sleep(1)
            except Exception as e:
                print("%s--链接--%s--发送异常:%s" % (phone, chat.entity.username, e))

                if str(e) == str(gourpBanStr) or str(e) == str(gourpBanStr2):
                    try:
                        await asyncio.sleep(60)
                        #await client(LeaveChannelRequest(channel=chat.entity.username))
                        print("当前时间--%s--%s--检测到被禁言,退出群组:%s" %
                              (time.strftime('%H:%M:%S'),phone, chat.entity.username))
                        await asyncio.sleep(60)
                        ii += 1
                    except Exception as e:
                        print("%s--%s--退群出现异常:%s" %
                              (phone, chat.entity.username, e))
                        ii += 1
                elif str(groupBanstr3) in str(e):

                    if detect_banned == True:
                        try:
                            await client(LeaveChannelRequest(channel=chat.entity.username))
                            print("%s--检测到被banned,退出群组:%s" %
                                  (phone, chat.entity.username))
                            ii += 1
                            banned += 1
                        except Exception as e:
                            print("%s--%s--被banned退群出现异常:%s" %
                                  (phone, chat.entity.username, e))
                            ii += 1
                            banned += 1
                        finally:
                            # 检测出现banned的情况
                            if banned > 10:
                                try:
                                    await client.disconnect()
                                except Exception as e:
                                    print(phone, '----', e)

                                running_abnormal_account += 1
                                task.cancel()
                                print('%s--开启banned检测后发现异常,任务已被结束--运行时异常账号数%s个' %
                                      (phone, running_abnormal_account))

                                await asyncio.sleep(60000)

                    elif detect_banned == False:
                        print("%s--检测到被banned,链接:%s" %
                              (phone, chat.entity.username))
                        banned += 1
                        if banned > 15:
                            try:
                                await client.disconnect()
                            except Exception as e:
                                print(phone, '----', e)

                            running_abnormal_account += 1
                            # glob获得路径下所有文件，可根据需要修改
                            src_file_list = glob(src_dir + phone + '.session*')
                            for srcfile in src_file_list:
                                mymovefile(srcfile, banned_dir)
                            task.cancel()
                            print('%s--banned出现异常,任务已被结束--运行时异常账号数%s' %
                                  (phone, running_abnormal_account))
                            await asyncio.sleep(60000)

                elif str(e) == str(groupBanstr4):
                    try:
                        await client(LeaveChannelRequest(channel=chat.entity.username))
                        print("%s--检测到异常,可能群组已消失.退出群组:%s" %
                              (phone, chat.entity.username))
                    except Exception as e:
                        print("%s--%s--检测到异常后，退群出现异常:%s" %
                              (phone, chat.entity.username, e))
                        ii += 1

                elif str(deletedstr) in str(e):
                    try:
                        await client.disconnect()
                    except Exception as e:
                        print(phone, '----', e)
                    running_abnormal_account += 1
                    # glob获得路径下所有文件，可根据需要修改
                    src_file_list = glob(src_dir + phone + '.session*')
                    for srcfile in src_file_list:
                        mymovefile(srcfile, account_banned_dir)
                    task.cancel()
                    print("%s--账号被禁,运行时异常账号数%s个--任务已被结束:%s" %
                          (phone, running_abnormal_account, e))
                    await asyncio.sleep(60000)

            finally:
                # 没开启banned检测则不会自动退群

                # if detect_banned == False and str(groupBanstr3) in str(e):
                #     await asyncio.sleep(15)
                #     print("jinru")
                # else:
                #     await asyncio.sleep(45)
                #     print("jinru2")
                await asyncio.sleep(60)

        # 发送退群事件，重新获取群组
        if ii > 0:
            chats = []
            try:
                async for dialog2 in client.iter_dialogs():
                    try:
                        if dialog2.entity.megagroup == True and dialog2.entity.username:
                            chats.append(dialog2)
                    except Exception as e:
                        pass
            except Exception as e:
                print("%s--发送退群事件,重新获取群组时发生异常:%s" % (phone, e))
            ii = 0
        # 发完一遍后等待一段时间
        i += 1
        if len(chats) > 5:
            randomMin = 50

            print("当前时间%s--%s--已发%s轮,间隔%s分钟,可用群数%s个" %
                  (time.strftime('%H:%M'), phone, i, randomMin, len(chats)))

            await asyncio.sleep(randomMin * 60)

    if len(chats) < 1:
        print("%s--无法获得会话框或是没有群组,导致异常并结束群发" % (phone))

    else:

        print("当前时间%s--%s结束发送" % (time.strftime('%H:%M:%S'), phone))

    try:

        await client.disconnect()

    except Exception as e:
        print("%s--断开连接出现异常:%s" % (phone, e))

#异步开启多帐号运行
async def tg_sendmessages_run():
    tasks = [asyncio.create_task(tg_sendmessages(
        account["phone"], account["api_id"], account["api_hash"])) for account in accounts]
    await asyncio.wait(tasks)
    print('全部账号群发完成')

#读取需要加群的群组链接
def openlink_txt():
    with open('groups.txt', 'r', encoding="utf-8") as f:
        txt = []
        groups = f.readlines()
        for group in groups:
            txt.append(group.strip())
        # print(len(link_txt))
        return txt

#加群时读取手机对应的json文件,并提示参数的缺失情况
async def join_group(phone, api_id, api_hash):
    global x
    global running_abnormal_account
    task = asyncio.current_task()

    try:
        with open(path + '/session/' + str(phone) + '.json', 'r', encoding='utf-8') as f:
            phoneJson = json.loads(f.read())

    except:
        print("对应json文件不存在----", phone)
        task.cancel()
        time.sleep(50000)
    #当json文件中的参数都存在时,直接跳过
    try:
        if (phoneJson["device"] and phoneJson["sdk"] and phoneJson["app_version"] and phoneJson["lang_code"] and phoneJson["system_lang_code"]):


            pass

    except:
        print("对应json文件的参数缺失----", phone)
        task.cancel()
        time.sleep(50000)
    #不走代理

    # client = TelegramClient(folder_session + phone, api_id, api_hash,lang_code=phoneJson["lang_pack"],
    #                         system_lang_code=phoneJson["system_lang_pack"])
    #走代理

    client = TelegramClient(folder_session + phone, api_id, api_hash, device_model=phoneJson["device"], system_version=phoneJson["sdk"],
                                app_version=phoneJson["app_version"], lang_code=phoneJson["lang_code"], system_lang_code=phoneJson["system_lang_code"])


    try:
        time.sleep(1)
        await client.connect()
    except Exception as e:
        print("%s--连接异常：%s" % (phone, e))
    if (await client.is_user_authorized()):
        print('%s--%s--成功登录' % (time.strftime('%H:%M:%S'), phone))
    else:
        task.cancel()
        print("{}--{}--无法正常登录,结束".format(time.strftime('%H:%M:%S'), phone))
        await asyncio.sleep(60000)

    j_join = 0
    # for link in groups_link:
    #当小于要加群的数量的时才执行
    while x < len(groups_link):

        #time.sleep(random.choice([3, 4, 5]))
        time.sleep(3)
        try:
            # playsound.playsound('test.mp3')
            x += 1
            print("当前时间%s,%s--正在进入群--%s" %
                  (time.strftime('%H:%M:%S'), phone, groups_link[x]))

            # 防止异步出错
            link = groups_link[x]
            #进群
            await client(JoinChannelRequest(link))

        except Exception as e:
            if str(deletedstr) in str(e):
                running_abnormal_account += 1
                task.cancel()
                print("%s--账号被禁,--运行时异常账号数%s--任务已被结束:%s" %
                      (phone, running_abnormal_account, e))
                await asyncio.sleep(60000)
            elif 'list index out of range' in str(e):
                print("群链接已用尽")

            else:
                print("%s--无法正常进群-- %s --:%s" % (phone, link, e))
                time.sleep(1)

        else:
            print("%s成功进群: %s 间隔180秒" % (phone, link))

            time.sleep(1)
            j_join += 1

        finally:

            await asyncio.sleep(180)
    print("%s共进%s个群" % (phone, j_join))

    try:

        await client.disconnect()
    except Exception as e:
        print("%s--断开连接时出现异常:%s" % (phone, e))


async def join_group_run():
    print("进群链接数:%s" % (len(groups_link)))
    tasks = [asyncio.create_task(join_group(
        account["phone"], account["api_id"], account["api_hash"])) for account in accounts]
    await asyncio.wait(tasks)
    print('全部账号进群完成')


if __name__ == '__main__':

    folder_session = 'session/'
    #是线程池还是设置异步单次的任务总数?
    #SEMAPHORE = asyncio.Semaphore(100)
    proxy = (socks.SOCKS5, '144.34.244.57', 2023, True, 'test123451', '476486d')
    
    j = 0
    x = -1
    lun = 0
    src_dir = './session/'
    account_banned_dir = './账号被禁/'  # 目的路径记得加斜杠
    banned_dir = './账号被禁言/'
    running_abnormal_account = 0
    #自动回复开关,默认关闭
    message_reply = False
    #群发前导出群链接开关,默认关闭
    write_link = False
    #禁言检测,默认关闭,关联到是否自动退群
    detect_banned = False
    #将session文件夹下的session号码写入json文件的开关,默认开启
    write_json = True
    path = os.path.dirname(os.path.realpath('__file__'))
    #将开始运行的日期写入
    with open('log.txt', 'w', encoding='utf-8') as f:
        shijian = str(datetime.date.today())
        f.write(shijian + '\n')
    # 从session文件夹中读取手机号并写入json
    # 打开日志
    # log=open('log.txt','a',encoding='utf-8')
    #savedStdout = sys.stdout

    try:
        if write_json:
            write_to_json()
    except:
        pass

    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
    #加error的等级信息写入error.log
    logging.basicConfig(filename="error.log", level=logging.ERROR)

    accounts = config['accounts']
    print('----------------------\n----------------------\n----------------------')
    print("Total account: " + str(len(accounts)))

    for var in accounts:
        print(var['phone'])
    print('----------------------\n----------------------\n----------------------')
    #分辨当前系统为windows还是linux
    if platform.system().lower() == 'windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    elif platform.system().lower() == 'linux':
        pass
    mode = input(
        "输入序号进行选择\n1.进群模式\n2.群发模式一:默认关闭\n3.群发模式二:自动回复\n4.群发模式三:批量退群\n5.群发模式四:群发前导出群链接\n")

    # 进群模式
    if mode == '1':
        print("启动中...")

        groups_link = openlink_txt()
        asyncio.run(join_group_run())
    # 群发模式
    elif mode == '2':
        round_mode = input("输入需要循环的次数\n按N退出\n")

        if round_mode == 'N':
            print("已退出")
        else:
            if round_mode.isnumeric():
                print("启动中...")
                lun = int(round_mode)
                asyncio.run(tg_sendmessages_run())
            else:
                print("输入格式不正确，已退出")

   # 群发模式二:自动回复
    elif mode == '3':

        round_mode = input("输入需要循环的次数\n按N退出\n")
        if round_mode == 'N':
            print("已退出")
        else:
            if round_mode.isnumeric():
                print("启动中...")
                message_reply = True
                lun = int(round_mode)
                asyncio.run(tg_sendmessages_run())
            else:
                print("输入格式不正确，已退出")

    # 群发模式三:批量退群
    elif mode == '4':
        round_mode = input("输入需要循环的次数\n按N退出\n")
        if round_mode == 'N':
            print("已退出")
        else:
            if round_mode.isnumeric():
                print("启动中...")
                detect_banned = True
                lun = int(round_mode)
                asyncio.run(tg_sendmessages_run())
            else:
                print("输入格式不正确，已退出")

    # 群发模式四:群发前导出群链接
    elif mode == '5':
        round_mode = input("输入需要循环的次数\n按N退出\n")
        if round_mode == 'N':
            print("已退出")
        else:
            if round_mode.isnumeric():
                print("启动中...")
                write_link = True
                lun = int(round_mode)
                asyncio.run(tg_sendmessages_run())
            else:
                print("输入格式不正确，已退出")

    else:
        print("输入错误，已退出")

    print("%s--停止运行" % (time.strftime('%H:%M:%S')))
