import requests
import json
import pprint
import re
from tqdm import tqdm
import time
import os

session = requests.session()
ico = {}
videoInfos = []
# 视频标题上是否添加P？ 比如p1,p2,p3。。。
title_p = True

cookie = "buvid3=A49942DB-EAB9-AFB1-210B-755ACEFB7EB623468infoc; b_nut=1676856923; i-wanna-go-back=-1; _uuid=8C3E2A53-E579-9369-8D67-DD794DD781CB20066infoc; buvid4=8715DE48-44D0-A576-8291-ACA539022FD424825-023022009-tCWJsLv7ShjcYRN9hp3Ypg%3D%3D; DedeUserID=304670947; DedeUserID__ckMd5=cc71dbedfcfeb12c; rpdid=|(u)~l~u~uuu0J'uY~Y)lYmmR; b_ut=5; header_theme_version=CLOSE; buvid_fp_plain=undefined; is-2022-channel=1; nostalgia_conf=-1; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; CURRENT_PID=93d78e70-cfae-11ed-b0d1-b31627e523ef; FEED_LIVE_VERSION=V8; home_feed_column=5; CURRENT_QUALITY=80; fingerprint=310de723bb1ae1f56b09fb42a7d404da; buvid_fp=d47d4c6a5bccd99ae5715c78a93f9fff; browser_resolution=1536-714; share_source_origin=WEIXIN; bsource=share_source_weixinchat; SESSDATA=cfaed98e%2C1701492946%2Ce16a7%2A61; bili_jct=4b105fae6ceb95eb7fb650ae1ede9727; sid=70ehntbl; innersign=0; bp_video_offset_304670947=803613936146448400; b_lsid=E24610674_1888A3FD9D1; PVID=2"


# cookie登录账号
def cookieLogin():
    url = "https://api.bilibili.com/x/space/myinfo"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55",
        "cookie": cookie
    }

    res = session.get(url=url, headers=headers).text
    myJSON = json.loads(res)
    userName = myJSON["data"]["name"]
    vipStatus = myJSON["data"]["vip"]["status"]
    if vipStatus == 0:
        vipStatus = "非会员"
    else:
        vipStatus = "大会员"
    # pprint.pprint(myJSON)
    print("您的账号名：" + userName + ",当前为：" + vipStatus)


# 获取视频数据
def getVideDate(bv):
    url = "https://api.bilibili.com/x/web-interface/view?bvid=" + bv
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55",
        "cookie": cookie
    }
    viderJSON = json.loads(session.get(url=url, headers=headers).text)
    ico["video"] = viderJSON["data"]["pic"]
    ico["up"] = viderJSON["data"]["owner"]["face"]

    video = viderJSON["data"]["pages"]
    print("正在获取视频数据\n视频标题：" + viderJSON["data"]["title"])

    for i in tqdm(range(len(video))):
        url = "http://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv}&qn={qn}".format(cid=video[i]["cid"], bv=bv,
                                                                                            qn=80)
        res = session.get(url=url, headers=headers).text
        res = json.loads(res)

        videoInfo = {}
        videoInfo["url"] = res["data"]["durl"][0]["url"]
        if title_p:
            videoInfo["title"] = f'P{str(video[i]["page"])} {video[i]["part"]}'
        else:
            videoInfo["title"] = video[i]["part"]

        if res["data"]["quality"] == 116:
            videoInfo["quality"] = "高清 1080P60"
        elif res["data"]["quality"] == 80:
            videoInfo["quality"] = "高清 1080P"
        elif res["data"]["quality"] == 64:
            videoInfo["quality"] = "高清 720P"
        elif res["data"]["quality"] == 32:
            videoInfo["quality"] = "清晰 480P"
        elif res["data"]["quality"] == 16:
            videoInfo["quality"] = "流畅 360P"
        global videoInfos
        videoInfos.append(videoInfo)
        # print(i,url,video[i]["part"])
        # print(i,videoInfo)
        time.sleep(0.2)
    # pprint.pprint(videoInfos)
    print("视频数据获取完成\n")


# 打印视频数据
def printVideoDate():
    if videoInfos == []:
        print("未找到视频数据，请先获取视频数据！")
        return
    for i in range(len(videoInfos)):
        video = videoInfos[i]
        print(str(i + 1) + "：" + video["title"] + " " + video["quality"])


# 下载视频
def downVideo(dir, num):
    # 文件夹不存在，则创建文件夹
    folder = os.path.exists(dir)
    # print(os.getcwd())
    if not folder:
        os.makedirs(dir)

    url = videoInfos[num]["url"]
    videoName = videoInfos[num]["title"] + " " + videoInfos[num]["quality"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55",
        "referer": "https://www.bilibili.com"
    }
    res = session.get(url=url, headers=headers, stream=True)
    total_size = int(int(res.headers["Content-Length"]) / 1024 + 0.5)

    with open(dir + videoName + ".flv", "wb") as f:
        print('开始下载文件：{},当前文件大小：{}KB'.format(videoName, total_size))
        for chunk in tqdm(res.iter_content(1024), total=total_size, unit='k', desc='Downloading'):
            f.write(chunk)
    print(videoName, "下载完毕")


def showMenu():
    print("0: 显示菜单\n1: 获取视频数据\n2: 打印视频数据\n3: 下载视频\n-1: 退出程序")


if __name__ == "__main__":
    cookieLogin()
    print()
    showMenu()
    #    bv="BV1eT4y1Z7T7"

    while (True):
        i = input("请输入功能菜单编号：")
        if i == '-1':
            break
        elif i == '0':
            showMenu()
        elif i == '1':
            if len(videoInfos) > 0:
                _op = input('当前系统内存有其他的视频，将会删除之前的视频，请确认是否继续？输入任意键继续，输入q退出')
                if _op == 'q' or _op == 'Q':
                    continue
                else:
                    print(f'清空内存数据')
                    videoInfos.clear()
            bv = input("请输入BV号：")
            getVideDate(bv)
            printVideoDate()
        elif i == '2':
            printVideoDate()
        elif i == '3':
            num = input("请输入要下载的编号(多个视频写成数组形式，例如：[1,2,3]),默认为下载所有视频：")
            dir = input("请输入保存路径，默认为./download/:")
            if dir == '':
                dir = "./download/"
            if (num == ''):
                print("预下载视频" + str(len(videoInfos)) + '个')
                for i in range(len(videoInfos)):
                    downVideo(dir=dir, num=i)
            elif (isinstance(eval(num), int)):
                downVideo(dir=dir, num=int(num) - 1)
            elif (isinstance(eval(num), list)):
                print("预下载视频" + str(len(eval(num))) + '个')
                for i in eval(num):
                    downVideo(dir=dir, num=i - 1)
        elif i == '':
            pass

    print("退出成功")
