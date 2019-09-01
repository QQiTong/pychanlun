#!/usr/bin/python3

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

my_sender = 'java_boss@mail.zyaoxin.com'  # 发件人邮箱账号
my_pass = 'LiangHua123456'  # 发件人邮箱密码
my_user = ['236819579@qq.com', '1106628276@qq.com']  # 收件人邮箱账号，我这边发送给自己


class Mail:
    def send(self, content):
        ret = True
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = formataddr(["reminder", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            # msg['To'] = my_user  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = "PyChanlun Future Remind"  # 邮件的主题，也可以说是标题
            server = smtplib.SMTP_SSL("smtpdm.aliyun.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            for i in range(len(my_user)):
                msg['To'] = my_user[i]
                server.sendmail(my_sender, my_user[i], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print(Exception)
            ret = False
        return ret

    # ret = mail()
    # if ret:
    #     print("邮件发送成功")
    # else:
    #     print("邮件发送失败")
# mail = Mail();
# mailResult = mail.send("这个测试邮件1")
# if not mailResult:
#     print("发送失败")