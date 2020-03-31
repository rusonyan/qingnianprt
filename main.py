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
from datetime import datetime, timedelta, timezone
import psycopg2


def get_image(path):

    image = None
    if path.startswith("http"):
        res = requests.get(path)
        image = Image.open(io.BytesIO(res.content))
    else:
        image = Image.open(path)
    return image


def image2bytes(image):
    """图片转二进制"""
    img_bytes = io.BytesIO()
    image.save(img_bytes, image.format)
    return img_bytes.getvalue()


app = Flask(__name__)


@app.route("/abcdefghgklmn", methods=["GET"])
def index():
    now = datetime.now().astimezone(timezone(timedelta(hours=8)))

    weeks = int(now.strftime("%w"))
    days = int(now.strftime("%d"))

    if weeks == 1 or weeks== 2:
        res = requests.get("http://news.cyol.com/node_67071.htm")
        res.encoding = "utf-8"
        #发布日期
        m = re.findall(
            r"(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)",
            res.text,
        )

        status = False
        if int(m[0][5]) == days:

            DATABASE_URL = os.environ['DATABASE_URL']

            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            cur.execute("SELECT week from SBDAXUEXI")
            endget = cur.fetchall()

            if endget[0][0] != days:
                status = True
                ENDEND = "UPDATE SBDAXUEXI set WEEK = " + str(
                    days) + " where ID=1"
                cur.execute(ENDEND)
                conn.commit()
                conn.close()

            

        if status == True:
            m = re.findall(r"<h3><a href=\"(.*?)\" target=\"_blank\">",
                           res.text)

            dicts = {
                1: "一",
                2: "二",
                3: "三",
                4: "四",
                5: "五",
                6: "六",
                7: "七",
                8: "八",
                9: "九",
                10: "十",
                11: "十一",
                12: "十二",
                13: "十三",
                14: "十四",
            }

            allit = re.findall(r"daxuexi/daxuex(.*?)/index\.html", m[0])
            lastgo = re.findall(r"\w(\d{0,2})", allit[0])
            season = int(lastgo[0])
            times = int(lastgo[1])

            seasons = dicts.get(season)
            timess = dicts.get(times)

            imgurl = re.findall(r"(.*?)/index.html", m[0])
            imgurls = imgurl[0] + "/images/icon.jpg"

            cover = get_image(imgurls)
            im = Image.open("ruson.jpg")
            draw = ImageDraw.Draw(im)
            setFont = ImageFont.truetype("Sou.otf", 30)
            draw.text(
                (272, 1073),
                "满分！我完成了“青年大学习”网上主题团课第" + seasons + "季第",
                font=setFont,
                fill=(0, 0, 0),
            )
            draw.text((272, 1117),
                      timess + "期，你也来试试吧",
                      font=setFont,
                      fill=(0, 0, 0))

            cover.thumbnail((100, 100))
            im.paste(cover, (149, 1056))
            sp = "./static/end.png"
            im.save(sp, "png")

            msg = MIMEMultipart()
            with open("./static/end.png", "rb") as f:
                mime = MIMEBase("image", "png", filename="print.png")
                # 加上必要的头信息:
                mime.add_header("Content-Disposition",
                                "attachment",
                                filename="print.png")
                mime.add_header("Content-ID", "<0>")
                mime.add_header("X-Attachment-Id", "0")
                # 把附件的内容读进来:
                mime.set_payload(f.read())
                # 用Base64编码:
                encoders.encode_base64(mime)
                # 添加到MIMEMultipart:
                msg.attach(mime)

            header = "第" + seasons + "季第" + timess + "期"
            msg["Subject"] = Header(header, "utf-8").encode()
            msg.attach(MIMEText("send with file...", "plain", "utf-8"))

            from_addr = "rusyan@sina.com"
            msg["From"] = Header(from_addr)
            password = "4703aaacb98c70b4"
            to_addr = "rusonyan@qq.com"
            smtp_server = "smtp.sina.com"
            server = smtplib.SMTP(smtp_server, 25)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())

 
            server.quit()

            return "发送完成" + str(days)
        else:
                return "今日份已完成"

    else:
        return "今天不是大学习更新的日子欧!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
