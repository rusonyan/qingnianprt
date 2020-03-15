import requests
import re
import os
import io
from PIL import Image, ImageFont, ImageDraw
from flask import Flask, request, render_template, send_file
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr


def get_image(path):

    image = None
    if path.startswith('http'):
        res = requests.get(path)
        image = Image.open(io.BytesIO(res.content))
    else:
        image = Image.open(path)
    return image


def image2bytes(image):
    '''图片转二进制'''
    img_bytes = io.BytesIO()
    image.save(img_bytes, image.format)
    return img_bytes.getvalue()


app = Flask(__name__)
@app.route('/', methods=['GET'])
def index():

    res = requests.get('http://news.cyol.com/node_67071.htm')
    res.encoding = 'utf-8'
    m = re.findall(r'<h3><a href=\"(.*?)\" target=\"_blank\">', res.text)

    dicts = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七',
             8: '八', 9: '九', 10: '十', 11: '十一', 12: '十二', 13: '十三', 14: '十四'}

    allit = re.findall(r'daxuexi/daxuex(.*?)/index\.html', m[0])
    lastgo = re.findall(r'\w(\d{0,2})', allit[0])
    season = int(lastgo[0])
    times = int(lastgo[1])

    seasons = dicts.get(season)
    timess = dicts.get(times)

    imgurl = re.findall(r'(.*?)/index.html', m[0])
    imgurls = imgurl[0]+'/images/icon.jpg'

    cover = get_image(imgurls)
    im = Image.open('root.jpg')
    draw = ImageDraw.Draw(im)
    setFont = ImageFont.truetype('Sou.otf', 30)
    draw.text((272, 1073), '满分！我完成了“青年大学习”网上主题团课第'+seasons+'季第',
              font=setFont, fill=(0, 0, 0))
    draw.text((272, 1117), timess+'期，你也来试试吧',
              font=setFont, fill=(0, 0, 0))

    cover.thumbnail((100, 100))
    im.paste(cover, (149, 1056))
    sp = './static/end.png'
    im.save(sp, 'png')

    msg = MIMEMultipart()
    with open('./static/end.png', 'rb') as f:
        mime = MIMEBase('image', 'png', filename='print.png')
        # 加上必要的头信息:
        mime.add_header('Content-Disposition',
                        'attachment', filename='print.png')
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(f.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        msg.attach(mime)

    msg['Subject'] = Header('来了……', 'utf-8').encode()
    msg.attach(MIMEText('send with file...', 'plain', 'utf-8'))

    from_addr = 'rusyan@sina.com'
    msg['From'] = Header(from_addr)
    password = '4703aaacb98c70b4'
    to_addr = 'rusonyan@qq.com'
    smtp_server = 'smtp.sina.com'
    server = smtplib.SMTP(smtp_server, 25)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

    return render_template('respon.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
