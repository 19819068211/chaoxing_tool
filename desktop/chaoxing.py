#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json
import re
import threading
from queue import Queue
from urllib import parse

import tkinter
import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.simpledialog
from tkinter import filedialog

from pyDes import des, PAD_PKCS5
import binascii
import os
import requests
import time
from lxml import etree

global video_url_list
video_url_list = []
class_list = []
global_headers = {}
course_dict = {}

# pwd DES 加密
def des_pwd(msg, key):
    des_obj = des(key, key, pad=None, padmode=PAD_PKCS5)
    secret_bytes = des_obj.encrypt(msg, padmode=PAD_PKCS5)
    return binascii.b2a_hex(secret_bytes)

# 视频任务enc校验计算
def encode_enc(clazzid: str, duration: int, objectId: str, otherinfo: str, jobid: str, userid: str, currentTimeSec: str):
    import hashlib
    data = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][0_{7}]".format(clazzid, userid, jobid, objectId, int(currentTimeSec) * 1000, "d_yHJ!$pdA~5", duration * 1000, duration)
    print(data)
    return hashlib.md5(data.encode()).hexdigest()


# 手机号登录，返回response
def sign_in(uname: str, password: str):
    sign_in_url = "https://passport2.chaoxing.com/fanyalogin"
    sign_in_data = "fid=314&uname={0}&password={1}&refer=http%253A%252F%252Fi.mooc.chaoxing.com&t=true".format(uname, des_pwd(password, "u2oh6Vu^").decode("utf-8"))
    sign_in_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '98',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'route=3744838b34ea6b4834cd438e19ed44f0; JSESSIONID=9CD969F9C1B9633A46EAD7880736DD51; fanyamoocs=11401F839C536D9E; fid=314; isfyportal=1; ptrmooc=t',
        'Host': 'passport2.chaoxing.com',
        'Origin': 'https://passport2.chaoxing.com',
        'Referer': 'https://passport2.chaoxing.com/login?loginType=4&fid=314&newversion=true&refer=http://i.mooc.chaoxing.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'X-Requested-With': 'XMLHttpRequest'
    }
    sign_in_rsp = requests.post(url=sign_in_url, data=sign_in_data, headers=sign_in_headers)
    return sign_in_rsp


# 任务1：用户登录，并合并cookie
def step_1(uname, password, lgw, text_log, list_classes):      
    sign_in_rsp = sign_in(uname, password)
    sign_in_json = sign_in_rsp.json()
    if sign_in_json['status'] == False:
        tkinter.messagebox.showerror('错误', '登陆失败！')
        sign_sus = False
        return False
    else:
        sign_sus = True
        tkinter.messagebox.showinfo('提示', '登录成功！') 
    global cookieStr, uid, global_headers
    uid = sign_in_rsp.cookies['_uid']
    cookieStr = ''
    for item in sign_in_rsp.cookies:
        cookieStr = cookieStr + item.name + '=' + item.value + ';'
    global_headers = {
        'Cookie': cookieStr,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    text_log.set("已登录")
    lgw.destroy()
    step_2(list_classes)
    return True


# 任务2：课程读取，并输出课程信息
def step_2(list_classes):
    class_url = "http://mooc1-2.chaoxing.com/visit/courses"
    class_rsp = requests.get(url=class_url, headers=global_headers)
    if class_rsp.status_code == 200:
        class_HTML = etree.HTML(class_rsp.text)
        tkinter.messagebox.showinfo('提示', '处理成功！') 
        i = 0
        global course_dict
        course_dict = {}
        for class_item in class_HTML.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            try:
                class_item_name = class_item.xpath("./div[2]/h3/a/@title")[0]
                # 等待开课的课程由于尚未对应链接，所以缺少a标签。
                i += 1
                course_dict[i] = [class_item_name, "https://mooc1-2.chaoxing.com{}".format(class_item.xpath("./div[1]/a[1]/@href")[0])]
                list_classes.insert(tkinter.END, class_item_name)
            except:
                pass
        # TODO: new API
        # class_url = "http://mooc2-ans.chaoxing.com/visit/courses/list?v=1649759111895&rss=1&start=0&size=500&catalogId=0&searchname="
        # class_rsp = requests.get(url=class_url, headers=global_headers)
        # if class_rsp.status_code == 200:
        #     class_HTML = etree.HTML(class_rsp.text)
        #     os.system("cls")
        #     print("处理成功，您当前已开启的课程如下：\n")
        #     i = 0
        #     global course_dict
        #     course_dict = {}
        #     for class_item in class_HTML.xpath('/html/body/div[3]/ul[1]/li'):
        #         try:
        #             class_item_name = class_item.xpath("./div[2]/h3/a/span/@title")[0]
        #             # 等待开课的课程由于尚未对应链接，所以缺少a标签。
        #             i += 1
        #             print(class_item_name)
        #             course_dict[i] = [class_item_name, class_item.xpath("./div[2]/h3/a/@href")[0]]
        #         except:
        #             pass
    else:
        tkinter.messagebox.showerror('课程处理失败')
    # print(course_dict)
    return course_dict


# 获取url重定向后的新地址与cpi
def url_302(oldUrl: str):
    # 302跳转，requests库默认追踪headers里的location进行跳转，使用allow_redirects=False
    course_302_rsp = requests.get(url=oldUrl, headers=global_headers, allow_redirects=False)
    new_url = course_302_rsp.headers.get("Location")
    if new_url == None:
        new_url = oldUrl
    result = parse.urlparse(new_url)
    new_url_data = parse.parse_qs(result.query)
    try:
        cpi = new_url_data.get("cpi")[0]
    except:
        print("fail to get cpi")
        cpi = None
    return {"new_url": new_url, "cpi": cpi}


# 获取所有课程信息
def course_get(url: str):
    course_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    course_rsp = requests.get(url=url, headers=course_headers)
    course_HTML = etree.HTML(course_rsp.text)
    return course_HTML


# 递归读取章节
def recursive_course(course_unit_list, chapter_mission, level):
    for course_unit in course_unit_list:
        h3_list = course_unit.xpath("./h3")
        for h3_item in h3_list:
            chapter_status = __list_get(h3_item.xpath("./a/span[@class='icon']/em/@class"))
            if chapter_status == "orange":
                print("--" * level, __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")), "      ", __list_get(h3_item.xpath("./a/span[@class='icon']/em/text()")))
                chapter_mission.append("https://mooc1-2.chaoxing.com{}".format(__list_get(h3_item.xpath("./a/@href"))))
            else:
                print("--" * level, __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")), "      ", chapter_status)
        chapter_item_list = course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course(chapter_item_list, chapter_mission, level + 1)


# thread
def createQueue(urls):
    urlQueue = Queue()
    for url in urls:
        urlQueue.put(url)
    return urlQueue


class spiderThread(threading.Thread):
    def __init__(self, threadName, urlQueue, cpi):
        super(spiderThread, self).__init__()
        self.threadName = threadName
        self.urlQueue = urlQueue
        self.cpi = cpi

    def run(self):
        while True:
            if self.urlQueue.empty():
                break
            chapter = self.urlQueue.get()
            deal_misson([chapter], self.cpi, 0)
            time.sleep(0.2)


def createThread(threadCount, urlQueue, cpi):
    threadQueue = []
    for i in range(threadCount):
        spiderThreading = spiderThread("threading_{}".format(i), urlQueue=urlQueue, cpi=cpi)  # 循环创建多个线程，并将队列传入
        threadQueue.append(spiderThreading)  # 将线程放入线程池
    return threadQueue


# 选取有任务点的课程,并处理
def deal_course_select(url_class, main, progress):
    new_url_dict = url_302(url_class)
    new_url = new_url_dict["new_url"]
    course_HTML = course_get(new_url)
    # 为防止账号没有课程或没有班级，需要后期在xpath获取加入try，以防报错
    chapter_mission = []
    try:
        course_unit_list = course_HTML.xpath("//div[@class='units']")
        for course_unit in course_unit_list:
            recursive_course(course_unit.xpath("./div"), chapter_mission, 1)
    except Exception as e:
        tkinter.messagebox.showerror('错误', e)
    # if len(chapter_mission) > 20:
    #     print("章节数大于20，已为您自动启动多线程")
    #     threadQueue = createThread(6, createQueue(chapter_mission), new_url_dict["cpi"])
    #     for thread in threadQueue:
    #         thread.start()  # 线程池启动
    #     for thread in threadQueue:
    #         thread.join()  # 线程池销毁
    # else:
    deal_misson(chapter_mission, new_url_dict["cpi"], 0, main, progress)


# 递归读取所有课程信息，返回dict
def recursive_course_dict(course_unit_list, chapter_dict):
    for course_unit in course_unit_list:
        h3_list = course_unit.xpath("./h3")
        for h3_item in h3_list:
            chapter_dict.update({__list_get(h3_item.xpath("./a/span[@class='chapterNumber']/text()")) + __list_get(h3_item.xpath("./a/span[@class='articlename']/span[@class='chapterNumber']/text()")) + __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")): __list_get(h3_item.xpath("./a/@href"))})
        chapter_item_list = course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course_dict(chapter_item_list, chapter_dict)


chapter_list = []
new_url_dict = None


def print_chapters(url_class, list_chapters) :
    global new_url_dict
    new_url_dict = url_302(url_class)
    new_url = new_url_dict["new_url"]
    course_HTML = course_get(new_url)
    i = 0
    chapter_dict = {}
    course_unit_list = course_HTML.xpath("//div[@class='units']")  # 课程中的大章节
    try:
        for course_unit in course_unit_list:
            recursive_course_dict(course_unit.xpath("./div"), chapter_dict)
        global chapter_list
        chapter_list = []
        list_chapters.delete(0, tkinter.END)
        for chapter_item in chapter_dict:
            i = i + 1
            try:
                list_chapters.insert(tkinter.END, chapter_item)
                chapter_list.append(chapter_dict[chapter_item])
            except Exception as e:
                print("chapter处理错误", e)
    except Exception as e:
        print(e)
    return new_url, chapter_list


# 获取所有的课程信息，并储存url
def deal_course_all(enter, main, progress):
    while True:
        try:
            url_chapter = chapter_list[int(enter) - 1]
            deal_misson([url_chapter], new_url_dict["cpi"], 1, main, progress)
            break
        except Exception as e:
            print("'%s'不是可识别的输入，请重新输入" % e)


# 读取章节页数
def read_cardcount(courseId: str, clazzid: str, chapterId: str, cpi: str):
    url = 'https://mooc1-2.chaoxing.com/mycourse/studentstudyAjax'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '87',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Origin': 'https://mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/mycourse/studentstudy?chapterId=357838590&courseId=214734258&clazzid=32360675&enc=ccf66103f539dfec439e4898b62c8024',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.60',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = "courseId={0}&clazzid={1}&chapterId={2}&cpi={3}&verificationcode=".format(courseId, clazzid, chapterId, cpi)
    rsp = requests.post(url=url, headers=headers, data=data)
    rsp_HTML = etree.HTML(rsp.text)
    card_count = 0
    try:
        card_count = rsp_HTML.xpath("//input[@id='cardcount']/@value")[0]
    except Exception as e:
        print("card count error", rsp.status_code, rsp.text, e)
    return card_count


# 处理video任务,校验为enc
def misson_video(objectId, otherInfo, jobid, name, reportUrl, clazzId):
    status_url = "https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectId)
    misson_headers = {
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0329-1945"
    }
    misson_headers.update(global_headers)
    status_rsp = requests.get(url=status_url, headers=misson_headers)
    status_json = None
    try:
        status_json = json.loads(status_rsp.text)
    except Exception as e:
        print("该视频任务点信息读取错误", status_rsp.status_code, status_url)
        return
    duration = status_json.get('duration')
    dtoken = status_json.get('dtoken')
    print(objectId, otherInfo, jobid, uid, name, duration, reportUrl)
    # multimedia_headers = {
    #     'Accept': '*/*',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/json',
    #     'Cookie': cookieStr,
    #     'Host': 'mooc1-1.chaoxing.com',
    #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    # }

    elses = "/{0}?clazzId={1}&playingTime={2}&duration={2}&clipTime=0_{2}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag=0&view=pc&enc={7}&rt=1&dtype=Video&_t={8}".format(dtoken, clazzId, duration, objectId, otherInfo, jobid, uid, encode_enc(clazzId, duration, objectId, otherInfo, jobid, uid, duration), int(time.time() * 1000))
    reportUrl_item = reportUrl + str(elses)
    video_url_list.append(reportUrl_item)
    # multimedia_rsp = requests.get(url=reportUrl_item, headers=multimedia_headers)
    print("检测到一个视频节点，已添加到任务列表")
    return reportUrl_item


# 处理live任务，核心为获取视频token
def misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzid):
    src = 'https://live.chaoxing.com/courseLive/newpclive?streamName=' + streamName + '&vdoid=' + vdoid + '&width=630&height=530' + '&jobid=' + jobid + '&userId={0}&knowledgeid={1}&ut=s&clazzid={2}&courseid={3}'.format(uid, chapterId, clazzid, courseId)
    rsp = requests.get(url=src, headers=global_headers)
    rsp_HTML = etree.HTML(rsp.text)
    token_url = rsp_HTML.xpath("//iframe/@src")[0]
    print(token_url)
    token_result = parse.urlparse(token_url)
    token_data = parse.parse_qs(token_result.query)
    token = token_data.get("token")
    finish_url = "https://zhibo.chaoxing.com/live/saveCourseJob?courseId={0}&knowledgeId={1}&classId={2}&userId={3}&jobId={4}&token={5}".format(courseId, chapterId, clazzid, uid, jobid, token[0])
    finish_rsp = requests.get(url=finish_url, headers=global_headers)
    print(finish_rsp.text)


# 处理document任务，核心为jtoken
def misson_doucument(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/pdf/index.html?v=2020-1103-1706',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/document?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc=1607066762782'.format(jobid, chapterId, courseid, clazzid, jtoken)
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 处理book任务，核心为jtoken
def misson_book(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 处理read任务，核心为jtoken
def misson_read(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/readv2?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    print(multimedia_rsp.text)


# 课程学习次数
def set_log(course_url: str):
    course_rsp = requests.get(url=url_302(course_url)["new_url"], headers=global_headers)
    course_HTML = etree.HTML(course_rsp.text)
    # TODO：人脸检测验证
    log_url = course_HTML.xpath("/html/body/script[11]/@src")[0]
    rsp = requests.get(url=log_url, headers=global_headers)
    print(rsp.text)


# 处理任务
def deal_misson(missons: list, class_cpi: str, mode: int, main, progress):
    for chapter_mission_item in missons:
        result = parse.urlparse(chapter_mission_item)
        chapter_data = parse.parse_qs(result.query)
        clazzId = chapter_data.get('clazzid')[0]
        courseId = chapter_data.get('courseId')[0]
        chapterId = chapter_data.get('chapterId')[0]
        cardcount = int(read_cardcount(courseId, clazzId, chapterId, class_cpi))
        for num in range(cardcount):
            try:
                medias_url = "https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(clazzId, courseId, chapterId, class_cpi, num)
                medias_rsp = requests.get(url=medias_url, headers=global_headers)
                medias_HTML = etree.HTML(medias_rsp.text)
                medias_text = medias_HTML.xpath("//script[1]/text()")[0]
                pattern = re.compile(r"mArg = ({[\s\S]*)}catch")
                datas = re.findall(pattern, medias_text)[0]
                datas = json.loads(datas.strip()[:-1])
                if mode == 0:
                    # mode 0 deal misson
                    medias_deal(datas, clazzId, chapterId, courseId, chapter_mission_item)
                else:
                    # mode 1 download medias
                    medias_download(datas["attachments"])
                progress['value'] += 3
                main.update()
            except Exception as e:
                tkinter.messagebox.showerror('错误',e)
                continue
    progress['value'] = 100
    tkinter.messagebox.showinfo('提示', '课程读取完成！') 

# 判断媒体类型并处理
def medias_deal(data, clazzId, chapterId, courseId, chapterUrl):
    result_json = data["attachments"]
    for media_item in result_json:
        if media_item.get("job") == None:
            continue
        media_type = media_item.get("type")
        jobid = media_item.get("jobid")
        if media_type == "video":
            objectId = media_item.get("objectId")
            otherInfo = media_item.get("otherInfo")
            name = media_item.get('property').get('name')
            url_video = misson_video(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=data["defaults"]["reportUrl"], clazzId=clazzId)
            # multimedia_headers = {
            #     'Accept': '*/*',
            #     'Accept-Encoding': 'gzip, deflate, br',
            #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            #     'Connection': 'keep-alive',
            #     'Content-Type': 'application/json',
            #     'Cookie': cookieStr,
            #     'Host': 'mooc1-1.chaoxing.com',
            #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
            #     'Sec-Fetch-Dest': 'empty',
            #     'Sec-Fetch-Mode': 'cors',
            #     'Sec-Fetch-Site': 'same-origin',
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
            # }
            # rsp = requests.get(url=url_video, headers=multimedia_headers)
            # print(rsp.text)
        elif media_type == "live":
            streamName = media_item.get("property").get("streamName")
            vdoid = media_item.get("property").get("vdoid")
            misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzId)
        elif media_type == "document":
            jtoken = media_item.get("jtoken")
            misson_doucument(jobid, chapterId, courseId, clazzId, jtoken)
        elif "bookname" in media_item["property"]:
            jtoken = media_item.get("jtoken")
            misson_book(jobid, chapterId, courseId, clazzId, jtoken)
        elif media_type == "read":
            jtoken = media_item.get("jtoken")
            misson_read(jobid, chapterId, courseId, clazzId, jtoken)


# 下载媒体
def medias_download(medias):
    downloads_dict = {}
    i = 0
    for media_item in medias:
        objectid = media_item.get("property").get("objectid")
        if objectid == None:
            continue
        status_rsp = requests.get(url="https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectid), headers=global_headers)
        status_json = json.loads(status_rsp.text)
        filename = status_json.get('filename')
        if status_json.get("pagenum") != None:
            download = status_json.get('pdf')
        else:
            download = status_json.get('http')
        i += 1
        downloads_dict[i] = [filename, download]
        print(i, ".       ", filename)
    if downloads_dict == {}:
        tkinter.messagebox.showinfo('提示', '所在章节无可下载的资源')
        return
    enter = input("请输入你要下载资源的序号，以逗号分隔：")
    enter_list = enter.split(",")
    download_headers = global_headers
    download_headers.update({
        "referer": "https://mooc1-2.chaoxing.com/ananas/modules/video/index.html?v=2021-0924-1446",
        "Host": "s1.ananas.chaoxing.com"
    })
    for media_index in enter_list:
        try:
            with open(downloads_dict[int(media_index)][0], "wb") as f:
                print("\n正在下载%s..." % downloads_dict[int(media_index)][0])
                rsp = requests.get(url=downloads_dict[int(media_index)][1], headers=download_headers, stream=True)
                length_already = 0
                length_all = int(rsp.headers['content-length'])
                for chunk in rsp.iter_content(chunk_size=5242880):
                    if chunk:
                        length_already += len(chunk)
                        print("\r下载进度：%d%%" % int(length_already / length_all * 100), end="", flush=True)
                        f.write(chunk)
                print("\n下载完成,其中PPT请手动修改后缀为PDF打开")
                f.close()
        except OSError:
            new_name = str(int(time.time())) + os.path.splitext(downloads_dict[int(media_index)][0])[-1]
            print("由于windows不允许文件包含特殊字符，已将文件重命名为 %s" % new_name)
            with open(new_name, "wb") as f:
                print("\n正在下载%s..." % new_name)
                length_already = 0
                length_all = int(rsp.headers['content-length'])
                for chunk in rsp.iter_content(chunk_size=5242880):
                    if chunk:
                        length_already += len(chunk)
                        print("\r下载进度：%d%%" % int(length_already / length_all * 100), end="", flush=True)
                        f.write(chunk)
                print("\n下载完成")
                f.close()
        except Exception as e:
            print("文件下载错误：", e)


def __list_get(list: list):
    if len(list):
        return list[0]
    else:
        return ""


class VideoThread(threading.Thread):
    def __init__(self, post_url, name, main, progress):
        super(VideoThread, self).__init__()
        self.post_url = post_url
        self.name = name
        self.main = main
        self.progress = progress

    def run(self) -> None:
        rsp = requests.get(url=self.post_url, headers=global_headers)
        cookieTmp = cookieStr
        for item in rsp.cookies:
            cookieTmp = cookieTmp + item.name + '=' + item.value + ';'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookieTmp,
            'Host': 'mooc1.chaoxing.com',
            'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2020-1105-2010',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
        }
        while True:
            # self.progress['value'] += 5
            # self.main.update()
            rsp = requests.get(url=self.post_url, headers=headers)
            if rsp.status_code != 200:
                print(self.post_url, self.name, "error!")
                self.post_url = self.post_url.replace("mooc1-2", "mooc1")
            else:
                print(self.name, rsp.text)
            time.sleep(60)


# 获取课程视频观看总时长
def get_task_status(url: str, main, progress):
    url = url_302(url)["new_url"]
    result = parse.urlparse(url)
    chapter_data = parse.parse_qs(result.query)
    courseId = chapter_data.get("courseId")[0]
    cpi = chapter_data.get("cpi")[0]
    clazzId = chapter_data.get("clazzid")[0]
    sta_url = "https://stat2-ans.chaoxing.com/task/s/index?courseid={0}&cpi={1}&clazzid={2}&ut=s&".format(courseId, cpi, clazzId)
    rsp = requests.get(url=sta_url, headers=global_headers)
    rsp_html = etree.HTML(rsp.text)
    already_time = float(__list_get(re.findall("[0-9]+[.]?[0-9]?", __list_get(rsp_html.xpath("//div[@class='fl min']/span/text()")))))
    all_time = float(__list_get(re.findall("[0-9]+[.]?[0-9]?", __list_get(rsp_html.xpath("//p[@class='bottomC fs12']/text()")))))
    print(already_time, "/", all_time)
    chapterId = False
    if already_time < all_time:
        datal_url = "https://stat2-ans.chaoxing.com/task/s/progress/detail?clazzid={0}&courseid={1}&cpi={2}&ut=s&page=1&pageSize=16&status=0".format(clazzId, courseId, cpi)
        rsp = requests.get(url=datal_url, headers=global_headers)
        for i in rsp.json()["data"]["results"]:
            for j in i["list"]:
                if j["type"] == "视频":
                    chapterId = j["chapterId"]
                    break
            if chapterId:
                break
        # print(chapterId)
        cardcount = int(read_cardcount(courseId, clazzId, chapterId, cpi))
        for i in range(cardcount):
            try:
                medias_url = "https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(clazzId, courseId, chapterId, cpi, i)
                medias_rsp = requests.get(url=medias_url, headers=global_headers)
                medias_HTML = etree.HTML(medias_rsp.text)
                medias_text = medias_HTML.xpath("//script[1]/text()")[0]
                pattern = re.compile(r"mArg = ({[\s\S]*)}catch")
                datas = re.findall(pattern, medias_text)[0]
                datas = json.loads(datas.strip()[:-1])
                for media_item in datas["attachments"]:
                    media_type = media_item.get("type")
                    jobid = media_item.get("jobid")
                    if media_type == "video":
                        objectId = media_item.get("objectId")
                        otherInfo = media_item.get("otherInfo")
                        name = media_item.get('property').get('name')
                        return VideoThread(misson_video(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=datas["defaults"]["reportUrl"], clazzId=clazzId), 
                        name=name, main=main, progress=progress)
                    else:
                        continue
            except Exception as e:
                tkinter.messagebox.showerror('错误', e)
                return 0
        tkinter.messagebox.showinfo('提示', '读取成功') 
        return 0


class video_nomal_thread(threading.Thread):
    def __list_get(self, list: list):
        if len(list):
            return list[0]
        else:
            return ""

    def __init__(self, url):
        super(video_nomal_thread, self).__init__()
        self.url = url
        self.all_time = int(re.findall("duration=\\d+&", url)[0][9:-1])
        self.multimedia_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookieStr,
            'Host': 'mooc1.chaoxing.com',
            'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2020-1105-2010',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
        }
        self.clazzId = self.__list_get(re.findall("(?<=clazzId=)\\d+", self.url))
        self.duration = self.__list_get(re.findall("(?<=duration=)\\d+", self.url))
        self.objectId = self.__list_get(re.findall("(?<=objectId=)[0-9a-zA-Z]+", self.url))
        self.otherInfo = self.__list_get(re.findall("(?<=otherInfo=)[a-z0-9A-Z_-]+", self.url))
        self.jobid = self.__list_get(re.findall("(?<=jobid=)\\d+", self.url))
        self.uid = self.__list_get(re.findall("(?<=userid=)\\d+", self.url))


    def run(self) -> None:
        rsp = requests.get(url=self.url_replace(0), headers=global_headers)
        print(rsp.status_code)
        cookieTmp = cookieStr
        for item in rsp.cookies:
            cookieTmp = cookieTmp + item.name + '=' + item.value + ';'
        self.multimedia_headers.update({"Cookie": cookieTmp})
        print("线程%s启动中，总任务时长%d秒" % (self.name, self.all_time))
        time_now = 60
        while time_now < self.all_time + 60:
            time.sleep(60)
            rsp = requests.get(url=self.url_replace(time_now), headers=self.multimedia_headers)
            print("线程%s运行中，当前时长:%d ,总时长:%d" % (self.name, time_now, self.all_time))
            time_now = time_now + 60

        rsp = requests.get(url=self.url_replace(self.all_time), headers=self.multimedia_headers)
        print("线程%s执行完成，任务状态:%s" % (self.name, rsp.text))

    def url_replace(self, now_time: int) -> str:
        enc_tmp = encode_enc(self.clazzId, int(self.duration), self.objectId, self.otherInfo, self.jobid, self.uid, str(now_time))
        url_tmp = re.sub("playingTime=\\d+", "playingTime=%d" % now_time, self.url)
        url_tmp = re.sub("enc=[0-9a-zA-Z]+", "enc=%s" % enc_tmp, url_tmp)
        return url_tmp


# 自定义任务类，处理菜单任务
class Things():
    def __init__(self, main, progress, list_classes, username='nobody'):
        self.username = username
        self.main = main
        self.progress = progress
        self.list_classes = list_classes

    # 下载课程
    def misson_1(self, list_chapters):
        while True:
            try: 
                enter = list_chapters.curselection()[0] + 1
                enter = int(enter)
                deal_course_all(enter, self.main, self.progress)
                tkinter.messagebox.showinfo('提示','课程处理完成！') 
                break
            except Exception as e:
                tkinter.messagebox.showerror('错误', e)
                return -1


    # 刷学习次数
    def misson_2(self):
        self.progress['value'] = 0
        while True:
            enter = self.list_classes.curselection()[0] + 1
            try:
                count = tkinter.simpledialog.askstring(title = 'ChaoXing Tool',prompt='请输入您要刷取的学习次数',initialvalue = '100')
                count = int(count)
                try:
                    try:
                        delay = tkinter.simpledialog.askstring(title = 'ChaoXing Tool'
                            ,prompt='未防止频次过快的次数刷取造成理论与实际误差较大，需要您手动指定每次次数刷取的间隔 请输入间隔时间(单位秒)：',initialvalue = '1')
                        delay = int(delay)
                    except:
                        tkinter.messagebox.showerror('错误 将使用默认时间', e)
                        delay = 1
                    for num in range(count):
                        set_log(course_dict[int(enter)][1])
                        time.sleep(delay)
                        self.progress['value'] += 100/count
                        self.main.update()
                    self.progress['value'] = 100
                    tkinter.messagebox.showinfo('提示','课程处理完成！') 
                    break
                except Exception as e:
                    tkinter.messagebox.showerror('错误', e)
                    return -1
            except Exception as e:
                tkinter.messagebox.showerror('错误', e)
                return -1


    # 刷取学习时间
    def misson_3(self):
        self.progress['value'] = 0
        self.main.update()
        tkinter.messagebox.showinfo('提示','时间可能较长(窗口可能无响应)，期间请不要关闭程序!')
        threadPool = []
        try:
            enter = self.list_classes.curselection()[0]
            isThread = get_task_status(course_dict[enter + 1][1], self.main, self.progress)
            if isThread:
                threadPool.append(isThread)
            for i in threadPool:
                i.start()
                time.sleep(10)
            for j in threadPool:
                j.join()
            self.progress['value'] = 100
            self.main.update()
            tkinter.messagebox.showinfo('提示','课程处理完成！')
        except Exception as e:
                tkinter.messagebox.showerror('错误',e)


    # 完成课程的任务点
    def misson_4(self):
        self.progress['value'] = 0
        while True:
            enter = self.list_classes.curselection()
            try:
                global video_url_list
                video_url_list = []
                for i in enter:
                    self.progress['value'] = 0
                    deal_course_select(course_dict[int(i+1)][1], self.main, self.progress)
                if len(video_url_list) == 0:
                    self.progress['value'] = 100
                    self.main.update()
                    tkinter.messagebox.showinfo('提示', '课程处理完成！') 
                else:
                    self.progress['value'] = 0
                    self.main.update()
                    speed = tkinter.messagebox.askquestion(title = 'Chaoxing Tool',message='立即完成(1秒即可完成视频任务点)？是--立刻 否--常规速度')
                    if speed == 'yes':
                        for item in video_url_list:
                            multimedia_headers = {
                                'Accept': '*/*',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                'Connection': 'keep-alive',
                                'Content-Type': 'application/json',
                                'Cookie': cookieStr,
                                'Host': 'mooc1-1.chaoxing.com',
                                'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
                                'Sec-Fetch-Dest': 'empty',
                                'Sec-Fetch-Mode': 'cors',
                                'Sec-Fetch-Site': 'same-origin',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
                            }
                            rsp = requests.get(url=item.replace("isdrag=0", "isdrag=4"), headers=multimedia_headers)
                            print(rsp.text)
                            self.progress['value'] += (100/len(video_url_list))
                            self.main.update()
                    else:
                        video_nomal_thread_pool = []
                        for video_item in video_url_list:
                            video_nomal_thread_pool.append(video_nomal_thread(video_item))
                        for item in video_nomal_thread_pool:
                            item.start()
                            time.sleep(1)
                            self.progress['value'] += 1
                            self.main.update()
                        tkinter.messagebox.showinfo('提示','视频线程已全部启动') 
                        for item in video_nomal_thread_pool:
                            item.join()

                    # 完成
                    self.progress['value'] = 100
                    self.main.update()
                    tkinter.messagebox.showinfo('提示','课程处理完成！') 
                break
            except Exception as e:
                tkinter.messagebox.showerror('错误', e)
                return -1

    # 获取作业
    def misson_5(self):
        dir = filedialog.asksaveasfile(initialdir = ".",filetypes=[('markdown','.md')])
        f = open(dir.name, 'a+', encoding="utf-8")
        f.write("> 作业批量导出 by chaoxing_tool   \n [github](https://github.com/liuyunfz/chaoxing_tool)   \n")
        self.progress['value'] = 0
        self.main.update()
        # 获取作业页面
        new_url_dict = url_302(course_dict[int(self.list_classes.curselection()[0] + 1)][1])
        new_url = new_url_dict["new_url"]
        try:
            course_HTML = course_get(new_url)
            res_list = course_HTML.xpath('//li/a[@title="作业"]/@data')
            work_url = 'https://mooc1-2.chaoxing.com' + res_list[0]
            parsed_result = parse.urlparse(work_url)
            query = dict(parse.parse_qsl(parsed_result.query))
            query.update(pageNum=1)
            prlist = list(parsed_result)
            prlist[4] = parse.urlencode(query)
            work_url = parse.ParseResult(*prlist).geturl()
        except Exception as e:
            tkinter.messagebox.showerror('错误', e)
            return -1
        nums  = 1
        work_page = course_get(work_url)
        try:
            # 翻页
            question_index = 1
            while len(work_page.xpath('////*[@id="RightCon"]/div/div/div[2]/ul/p')) == 0:
                work_page = course_get(work_url)
                url_parsed = parse.urlparse(work_url)
                query = dict(parse.parse_qsl(url_parsed.query))
                nums = nums + 1
                query['pageNum'] = str(nums)
                prlist = list(parsed_result)
                prlist[4] = parse.urlencode(query)
                work_url = parse.ParseResult(*prlist).geturl()
                # 作业列表
                work_list = work_page.xpath('//p[@class="clearfix"]/a[@class="Btn_blue_1 fr"]/@href')
                # 遍历作业
                for work in work_list:
                    workpage_url = 'https://mooc1.chaoxing.com' + work
                    question_page = course_get(workpage_url)
                    # 获取标题
                    title = question_page.xpath('/html/body/div[3]/div/div/div/div[1]/ul/li/a')
                    title[0].text = "#### " + title[0].text + "  "
                    f.write(title[0].text)
                    f.write("\n")
                    # 获取题目类型
                    type_question = question_page.xpath('//*[@id="ZyBottom"]/div[1]/h2/text()')
                    for cur_type in type_question:
                        # 单选题
                        if cur_type[2:] == "单选题":
                            # 提取单选题与其他类型题之间的内容
                            # 获取问题
                            question = question_page.xpath('//div[@style="width:80%;height:100%;float:left;"]')
                            # 选择
                            option = question_page.xpath('//a[@style="word-break: break-all;"]')
                            # 答案
                            answer = question_page.xpath('//div[@class="Py_answer clearfix"]/span[position()<2]')
                            # 防止数组溢出
                            if len(option)/4 != len(question) or len(answer) != len(question):
                                continue
                            index = 0
                            for i in range(len(question)):
                                j = 0
                                question[i].text = question[i].text.replace('\t', '')
                                question[i].text = question[i].text.replace('\n', '')
                                question[i].text = question[i].text.replace('\r', '')
                                question[i].text = question[i].text.replace('&nbsp;', '')
                                # 非空
                                if question[i].text == "" or question[i].text == None:
                                    question[i].text = question[i].xpath("./p")[0].text
                                question[i].text = "**" + str(question_index) +" "+ question[i].text + "**   "
                                f.write(question[i].text)
                                question_index = question_index + 1
                                f.write("\n")
                                while j < 4:
                                    if option[index].text != None:
                                        option[index].text = option[index].text + "   "
                                        f.write(option[index].text)
                                        f.write("\n")
                                    else:
                                        formula =  option[index].xpath(".//img/@src")
                                        # 非空
                                        if len(formula) == 0:
                                            index = index + 1
                                            j = j + 1
                                            continue
                                        # 图片的绝对地址
                                        elif formula[0][0] != 'h':
                                            formula[0] = 'https://mooc1.chaoxing.com' + formula[0]
                                        formula[0] = "![img](" + formula[0] + ")   "
                                        f.write(formula[0])
                                        f.write("\n")
                                    index = index + 1
                                    j = j + 1
                                answer[i].text = "> " + answer[i].text + "   "
                                f.write(answer[i].text)
                                f.write("\n\n")
                            self.progress['value'] += 5
                            self.main.update()
                        elif cur_type[2:] == "判断题":
                            # TODO 判断题爬取
                            pass
                        elif cur_type[2:] == "论述题":
                            # TODO 论述题爬取
                            pass
                        elif cur_type[2:] == "多选题":
                            # TODO 多选题爬取
                            pass
        except Exception as e:
            tkinter.messagebox.showerror('错误', e)
            return -1
        f.close()
        self.progress['value'] = 100
        self.main.update()
        tkinter.messagebox.showinfo('提示', '课程处理完成！')
        return 0


# main window class
class main_Window:
    def __init__(self):
        self.bit = True

    # before_start tip
    def before_start(self):
        bw = tkinter.Tk()
        bw.geometry('850x500')
        bw.title("ChaoXing Tool")
        bw.iconbitmap('chaoxing_icon.ico')

        txt = "欢迎您使用 chaoxing_tool , 本工具是针对超星(学习通)所编写的Python脚本工具\n" +  \
        "本工具完全免费且开源，项目地址: https://github.com/liuyunfz/chaoxing_tool\n" + \
        "使用前请确认您使用的是最新版，防止因为超星系统更新导致的功能失效\n"+ \
        "\n且确认以下须知与功能介绍\n" + \
        "1.本项目支持一键完成的任务点不包括考试与测试\n" + \
        "2.输入密码时会被自动隐藏，防止您的密码被偷窥\n" + \
        "3.项目不能完全保证不被系统识别异常，请理性使用\n" + \
        "4.所有功能均采用发送GET/POST请求包完成，效率更高且占用资源低\n" + \
        "5.完成课程任务点中的视频任务点会在最后统一处理，由用户决定完成方式\n" + \
        "6.其中快速完成可能会导致异常，而常规完成则会同步视频时长完成（需要保证软件保持开启状态）用于避免可能由时长\n带来的异常\n" + \
        "7.如果您在使用中有疑问或者遇到了BUG，请前往提交Issue: https://github.com/liuyunfz/chaoxing_tool/issues\n"+\
        "确认后正式使用本软件:\n"
        tkinter.Message(bw, text=txt, width = 1000, anchor = "w"
        , justify = "left", bg = "#E0FFFF", fg = "black").pack()
        tkinter.Button(bw, text="点击确认", command=bw.destroy, relief="groove").pack()

        bw.attributes("-alpha", 0.85)
        bw.config(background ="#E0FFFF")
        bw.mainloop()


    # creat main window
    def mainwin_create(self):
        # window
        self.main = tkinter.Tk()
        self.main.geometry('800x600')
        self.main.title("ChaoXing Tool")
        self.main.resizable()
        self.main.attributes("-alpha", 0.85)
        self.main.config(background ="#E0FFFF")
        self.main.iconbitmap('chaoxing_icon.ico')

        # 进度条
        progress = tkinter.ttk.Progressbar(self.main, length=200)
        progress.place(x = 300, y =500)
        progress['maximum'] = 100
        progress['value'] = 0

        # 显示课程
        list_classes = tkinter.Listbox(self.main, bg = "#E0FFFF", height = 20, width = 40, selectmode='extended')
        list_classes.place(x=5, y=70)

        self.things = Things(self.main, progress, list_classes)

        # 显示章节
        list_chapters = tkinter.Listbox(self.main, bg = "#E0FFFF", height = 20, width = 40)
        list_chapters.place(x=405, y =70)

        # 登录
        lgb = tkinter.Button(self.main, text="登录", command=lambda: self.login(text_log, list_classes), relief="groove")
        lgb.place(x=5, y=0)
        text_log = tkinter.StringVar()
        text_log.set("未登录")

        # 退出登录
        quit_log = tkinter.Button(self.main, text="退出当前账号，重新登陆", command=lambda:self.restart(), relief="groove")
        quit_log.place(x=5, y=35)

        # 登录状态提示
        log_tip = tkinter.Label(self.main, bg="#E0FFFF", textvariable=text_log)
        log_tip.place(x=55, y=0)

        # 获取章节
        get_chapters_bottom = tkinter.Button(self.main, text="获取章节", command=lambda:
        print_chapters(course_dict[int(list_classes.curselection()[0] + 1)][1], list_chapters), relief="groove")
        get_chapters_bottom.place(x=55, y=565)

        # 完成任务点
        complear_fewclass_bottom = tkinter.Button(self.main, text="完成课程中的任务节点（不包含测验）", command=lambda:
        self.things.misson_4(), relief="groove")
        complear_fewclass_bottom.place(x=125, y=565)

        # 下载
        download = tkinter.Button(self.main, text="下载课程资源", command=lambda:
        self.things.misson_1(list_chapters), relief="groove")
        download.place(x=385, y=565)

        # 刷学习次数
        Number_learningtimes = tkinter.Button(self.main, text="刷取课程学习次数", command=lambda:
        self.things.misson_2(), relief="groove")
        Number_learningtimes.place(x=485, y=565)

        # 刷学习时间
        Swipelearning = tkinter.Button(self.main, text="刷取视频学习时间", command=lambda:
        self.things.misson_3(), relief="groove")
        Swipelearning.place(x=619, y=565)

        # 获取作业
        homework = tkinter.Button(self.main, text="导出作业", command=lambda : self.things.misson_5(), relief="groove")
        homework.place(x=350, y=530)

        return self.main


    # login
    def login(self, text_log, list_classes):
        # Login window
        lgw = tkinter.Toplevel()
        lgw.geometry("300x300")

        # input tip
        account_input = tkinter.Label(lgw,text = "账号：",  bg="#E0FFFF")        
        password_input = tkinter.Label(lgw,text = "密码：", bg="#E0FFFF")        
        account_input.grid(row = 0)
        password_input.grid(row = 1)

        # input
        account = tkinter.Entry(lgw)
        password = tkinter.Entry(lgw, show = '*')
        account.grid(row=0, column=1)
        password.grid(row=1, column=1)

        # window
        lgw.attributes("-alpha",0.85)
        lgw.config(background ="#E0FFFF")
        lgb = tkinter.Button(lgw, text = "点击登录", command = lambda : step_1(account.get(), 
        password.get(), lgw, text_log, list_classes), relief="groove")
        lgb.grid(row=3, column=0, sticky="w", padx=10, pady=5)

    def restart(self):
        self.main.destroy()
        self.start()

    def start(self):
        self.before_start()
        minw = self.mainwin_create()
        minw.mainloop()


if __name__ == "__main__":
    mainwins= main_Window()
    mainwins.start()
