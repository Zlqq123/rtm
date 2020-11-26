import sys
sys.path.append('./')
import time
import xlsxwriter


def mail_sender(p_name='',filename=[]):
    import smtplib
    from email.mime.multipart import MIMEMultipart    
    from email.mime.text import MIMEText    
    from email.mime.image import MIMEImage 
    from email.header import Header 
    from personal_info import email_passaword

    username='xzml_zlq@163.com'
    password=email_passaword()
    sender='xzml_zlq@163.com'
    receiver=['Zhanglanqing@csvw.com']

    subject = 'Python email test'
    #通过Header对象编码的文本，包含utf-8编码信息和Base64编码信息。以下中文名测试ok
    #subject = '中文标题'
    #subject=Header(subject, 'utf-8').encode()

    #构造邮件对象MIMEMultipart对象
    #下面的主题，发件人，收件人，日期是显示在邮件页面上的。
    msg = MIMEMultipart('mixed') 
    msg['Subject'] = subject
    msg['From'] = 'xzml_zlq@163.com <xzml_zlq@163.com>'
    #收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
    msg['To'] = ";".join(receiver) 
    #msg['Date']='2012-3-16'

    #构造文字内容
    text = "Hi!\Your program "+ p_name+ " is finished, please check "
    text_plain = MIMEText(text,'plain', 'utf-8')
    msg.attach(text_plain)

    if filename!=[]:
        #构造附件
        sendfile=open(filename,'rb').read()
        text_att = MIMEText(sendfile, 'base64', 'utf-8') 
        text_att["Content-Type"] = 'application/octet-stream'  
        #以下附件可以重命名成aaa.txt
        #text_att["Content-Disposition"] = 'attachment; filename="aaa.txt"'
        #另一种实现方式
        text_att.add_header('Content-Disposition', 'attachment', filename='log.txt') #附件命名
        #以下中文测试不ok
        #text_att["Content-Disposition"] = u'attachment; filename="中文附件.txt"'.decode('utf-8')
        msg.attach(text_att) 


    #发送邮件
    smtp = smtplib.SMTP()    
    smtp.connect('smtp.163.com')
    #我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
    #smtp.set_debuglevel(1)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()

#mail_sender(r'D:\21python\log.txt')



def time_cost(filename=[]):
    '''
    在指定log文件中 print每个函数耗时
    '''
    def _t2(fn):
        def _wrapper(*args,**kwargs):
            if filename==[]:
                start=time.time()
                A=fn(*args,**kwargs)
                dt=time.time()-start
                if dt<60:
                    print("%s cost %s second"%(fn.__name__,round(dt,2)))
                elif dt<3600:
                    dm=int(dt/60)
                    dt=dt-dm*60
                    print("%s cost %s min %s second"%(fn.__name__,dm,round(dt,2)))
                else:
                    dh=int(dt/3600)
                    dm=int((dt-dh*3600)/60)
                    dt=dt-dh*3600-dm*60
                    print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,round(dt,2)))
            else:
                doc=open(filename,'a')
                start=time.time()
                A=fn(*args,**kwargs)
                dt=time.time()-start
                if dt<60:
                    print("%s cost %s second"%(fn.__name__,round(dt,2)),file=doc)
                elif dt<3600:
                    dm=int(dt/60)
                    dt=dt-dm*60
                    print("%s cost %s min %s second"%(fn.__name__,dm,round(dt,2)),file=doc)
                else:
                    dh=int(dt/3600)
                    dm=int((dt-dh*3600)/60)
                    dt=dt-dh*3600-dm*60
                    print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,round(dt,2)),file=doc)
                doc.close()
            return A
        return _wrapper
    return _t2

def time_cost_all(filename=[]):
    def t1(fn):
        num=[]
        def _wrapper(*args,**kwargs):
            if filename==[]:
                start=time.time()
                A=fn(*args,**kwargs)
                dt=time.time()-start
                num.append(dt)
                print("%s 第 %s 次执行  耗时 %s  s 总耗时 %s   min"%(fn.__name__,len(num),round(dt,2),round(sum(num)/60,2)))
            else:
                doc=open(filename,'a')
                start=time.time()
                A=fn(*args,**kwargs)
                dt=time.time()-start
                num.append(dt)
                print("%s 第 %s 次执行  耗时 %s  s 总耗时 %s   min"%(fn.__name__,len(num),round(dt,2),round(sum(num)/60,2)),file=doc)
                doc.close()
            return A
        return _wrapper
    return t1



def print_in_excel(aus,s1):
    workbook = xlsxwriter.Workbook(s1)
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(aus)):
        for j in range(len(aus[0])):
            worksheet.write(i+1,j,aus[i][j])
    workbook.close()