import requests
import re
import os
import io
import json
from flask import Flask, request, render_template, send_file
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr
from datetime import datetime, timedelta, timezone
import psycopg2


def gethb(hblist):
    link = re.findall(r'<a href=\"(.*?)\"', hblist)
    name = re.findall(r'title=\'(.*?)\'', hblist)
    return link[0], name[0]


def getpre(link):
    endlink = requests.get(link)
    endlink.encoding = 'utf-8'
    endlinkstr = re.findall(r'name=\"description\" content=\"(.*?)>',
                            endlink.text)
    return endlinkstr[0][:100]


def getprs(njlist):
    link = re.findall(r'(\d*).html', njlist)
    name = re.findall(r'_blank\">(.*)', njlist)
    links = 'http://info.ningjin.gov.cn/content/' + link[0] + '.html'
    return links, name[0]


class Hbset(object):
    def __init__(self, n, l, p):
        self.hbname = n
        self.hblink = l
        self.hbprev = p

    def print(self):
        return self.hbname, self.hblink, self.hbprev


app = Flask(__name__)


@app.route("/abcdefghgklmn", methods=["GET"])
def index():
    guojinew = ''
    hbset = []
    hbset.append(Hbset(' ', ' ', ' '))
    #新闻
    guojinews = []
    toutiao = requests.get(
        'https://way.jd.com/jisuapi/get?channel=国际&num=5&start=0&appkey=5e35c7cd0fe22478c66286b7596f2e68'
    )
    toutiao.encoding = 'utf-8'
    jsons = json.loads(toutiao.text)
    newslist = jsons['result']['result']['list'][0]['title']
    guojinews.append(jsons['result']['result']['list'][0]['title'])
    guojinews.append(jsons['result']['result']['list'][1]['title'])
    guojinews.append(jsons['result']['result']['list'][2]['title'])
    guojinews.append(jsons['result']['result']['list'][3]['title'])
    guojinews.append(jsons['result']['result']['list'][4]['title'])
    for x in range(5):
        guojinew = guojinew + str(x + 1) + '.  ' + guojinews[x] + '  '

    #建院
    hbre = requests.get("http://www.hebiace.edu.cn/col/col6/index.html")
    hbre.encoding = 'utf-8'
    hbre_get = re.findall(r'<div class=\"fl\"(.*?)div>', hbre.text)

    gotsql = 'http://www.hebiace.edu.cn/art/2020/3/27/art_6_14156.html'
    gotsql0 = 'http://info.ningjin.gov.cn/content/1783.html'
    gotsql1 = 'http://info.ningjin.gov.cn/content/16456.html'

    for x in range(10):
        link, name = gethb(hbre_get[x])
        if link == gotsql:
            break
        hbset.append(Hbset(name, link, getpre(link)))

    njtar = [
        'http://info.ningjin.gov.cn/channelList/11055.html',
        'http://info.ningjin.gov.cn/channelList/11072.html'
    ]

    for x in range(2):
        njre = requests.get(njtar[x])
        njre.encoding = 'utf-8'
        njre_get = re.findall(r'<a href=\"/content/(.*?)</a>', njre.text)
        for y in range(4):
            link, name = getprs(njre_get[y])
            if link == gotsql0 or link == gotsql1:
                break
            hbset.append(Hbset(name, link, name))

    try:
        name1, link1, prev1 = hbset[1].print()
    except IndexError as e:
        name1, link1, prev1 = hbset[0].print()
    try:
        name2, link2, prev2 = hbset[2].print()
    except IndexError as e:
        name2, link2, prev2 = hbset[0].print()
    try:
        name3, link3, prev3 = hbset[3].print()
    except IndexError as e:
        name3, link3, prev3 = hbset[0].print()
    try:
        name4, link4, prev4 = hbset[4].print()
    except IndexError as e:
        name4, link4, prev4 = hbset[0].print()
    return render_template(
        'index.htm',
        guojinew=guojinew,
        name1=name1,
        link1=link1,
        prev1=prev1,
        name2=name2,
        link2=link2,
        prev2=prev2,
        name3=name3,
        link3=link3,
        prev3=prev3,
        name4=name4,
        link4=link4,
        prev4=prev4,
    )


@app.route("/mail", methods=["GET"])
def index_x():
    #requests.get('https://qingnianprt.herokuapp.com/abcdefghgklmn')
    now = datetime.now().astimezone(timezone(timedelta(hours=8)))
    days = now.strftime("%d")
    mon = now.strftime("%m")
    header = mon + '月' + days + '号的日报来了！'
    
    a = requests.get('https://qingnianprt.herokuapp.com/abcdefghgklmn')
    a.encoding='utf-8'
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(a.text, 'html', 'utf-8'))
    msg["Subject"] = Header(header, "utf-8").encode()

    from_addr = "rusyan@sina.com"
    msg["From"] = Header(from_addr)
    msg['To'] = "闫瑞松"
    password = "4703aaacb98c70b4"
    to_addr = "rusonyan@qq.com"
    smtp_server = "smtp.sina.com"
    server = smtplib.SMTP(smtp_server, 25)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())

    server.quit()
    return "ok"
