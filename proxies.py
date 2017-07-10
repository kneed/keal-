import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import re
#proxiess={'https':'https://114.99.3.89:808'} #代理
url='http://www.xicidaili.com/nn'
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
proxies=[]
next_page_url=[]
def get_ips(res_url):
    global next_page_url
    pro_first = []  # 第一次获取
    pro_second = []  # 第二次筛选
    r=requests.get(res_url,headers=headers)#获取response
    soup=BeautifulSoup(r.text,'html.parser')#利用美丽汤解析
    ip_list=soup.find('table',id='ip_list')#找到所有ip的头标签
    for list in ip_list.find_all('tr',class_=True):
        for data in list.find_all('td',class_=False):
            pro_first.append(data.string)  #此次加入的包括了一些无用的数据
    i, j, k = 0,1, 3
    while k<len(pro_first):
        pro_second.append(pro_first[i])   #这次加入的是ip,端口，以及http或者Https
        pro_second.append(pro_first[j])
        pro_second.append(pro_first[k])
        i=i+6
        j=j+6
        k=k+6
        proxies.extend([pro_second[0],pro_second[1],pro_second[2]])
        pro_second.clear()
    print(len(proxies)/3)  #打印得到的IP地址
    next_page_url.append('http://www.xicidaili.com'+soup.find('a',class_='next_page').get('href'))

def store_into_sqlite():
    text_url='http://1212.ip138.com/ic.asp'
    conn = sqlite3.connect('ip_proxies')#连接到数据库
    cursors=conn.cursor() #建立光标，对光标进行操作
    print('open successfully')
   # cursors.execute('''CREATE TABLE IPs
   #         (IP    CHAR(50)  NOT NULL);''')   #创建表
    i,j,k=0,1,2
    while k<len(proxies):
        ip=proxies[k].lower()+'://'+proxies[i]+':'+proxies[j] #格式类似于 http://123.265.265.21:559
        head=proxies[k].lower()
        proxy=head+':'+ip
        test_proxy={head:ip}
        print(test_proxy)
        try:  #验证代理
            r=requests.get(text_url,headers=headers,proxies=test_proxy,timeout=5)
            r.encoding='gb2312'
            if re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',r.text):
                x=re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',r.text)[0]
            else:
                print('返回内容为空，返回码为：',r.status_code)
                i += 3
                j += 3
                k += 3
                continue
            print(str(x))
            print(str(proxies[i]))
            if x==proxies[i]:
                cursors.execute("insert into IPs Values(?)",[proxy])
                print('插入成功')
                conn.commit()
            else:
                print('此ip无效','错误代码：',r.status_code)
            i+=3
            j+=3
            k+=3
            time.sleep(1)
        except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectTimeout,requests.exceptions.ProxyError):
            print (test_proxy,'超时，继续下一个')
            i += 3
            j += 3
            k += 3
            continue
    proxies.clear()#在这里清楚掉第一页爬取的内容。

def main():
    get_ips(url)
    i = 0
    while i < len(next_page_url):
        store_into_sqlite()
        get_ips(next_page_url[i])
        time.sleep(random.randint(2,4))
        i += 1
        store_into_sqlite()

if __name__=='__main__':
    main()