"""
爬取百度贴吧中指定帖子中的所有图片——————requests-bs4-re路线
1.0,2.0,2.5,2.6,3.0
3.2
"""
import requests, os, re, time, random
from bs4 import BeautifulSoup

def get_proxies(path=r"D:\python\tieba_pics-crawler\proxies.txt"):
    global Proxies
    with open(path) as f:
        p = f.readlines()
        proxy = p.pop()
        if proxy[-1] == "\n":
            proxy = proxy[:-1]
    with open(path, "w") as f:
        for pr in p:
            f.write(pr)
    Proxies = {"http": "http://"+proxy,
               "https":"http://"+proxy}

headers = {
'Connection': 'close',
'Cache-Control': 'max-age=0',
'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
'sec-ch-ua-mobile': '?0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Sec-Fetch-Site': 'same-site',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-User': '?1',
'Sec-Fetch-Dest': 'document',
'Accept-Language': 'zh-CN,zh;q=0.9',
'Host': "tieba.baidu.com"
}

def getHTTPtext(url):
    time.sleep(1)
    try:
        r = requests.get(url, timeout=30, proxies=Proxies, verify=False, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        get_proxies()
        r = requests.get(url, timeout=30, proxies=Proxies, verify=False, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text


def add_link_list(html, link_list):
    soup = BeautifulSoup(html, "html.parser")
    list1 = soup("img", "BDE_Image")
    for i in list1:
        href = i.attrs['src']
        link_list.append(href)


def get_information(html, link_list, alist):
    soup = BeautifulSoup(html, "html.parser")
    list1 = soup("img", "BDE_Image")
    for i in list1:
        href = i.attrs['src']
        link_list.append(href)
    r2 = re.findall(r'<title>.*?_百度贴吧', html[:5000])
    r3 = r2[0].split("_")
    title = r2[0].split("_")[0][7:]
    if len(r3) == 3:
        ba_name = r3[1]
    else:
        r_1 = re.findall(r'【.*?】', r3[0])[-1]
        ba_name = r_1[1:][:-1]
    max_page = re.findall(r'\d+', re.findall(r'共.*?页', html)[0])[0]
    alist.append(title)
    alist.append(max_page)
    alist.append(ba_name)


def download_pic(link, count, path_now, len_link):
    path = path_now + str(count) + ".png"
    try:
        if not os.path.exists(path):
            r = requests.get(link, timeout=30, proxies=Proxies, verify=False, headers=headers)
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
                print("\r保存成功,这是第{}/{}张图片".format(count, len_link), end='')
        else:
            print("\r文件已存在", end='')
    except:
        get_proxies()
        print("保存失败")


def make_path(ba_name, title):
    a = input("文件路径是否使用默认设置?若否，输入从何处开始更改(从1开始)：")
    path_list = ['D', 'tieba_pics', ba_name, title[:15]]
    while a:
        a = int(a)
        b = input("现在在修改第{}层文件,输入文件名,回车以终止：".format(a))
        if not b:  # b为空则终止
            break
        if a <= 4:
            path_list[a - 1] = b
        else:
            path_list.append(b)
        a += 1
    c = 1
    path_now = path_list[0] + "://"
    while c + 1 <= len(path_list):
        path_now = path_now + path_list[c] + "//"
        if not os.path.exists(path_now):
            os.mkdir(path_now)
        c += 1
    return path_now


def real_link(link_list):
    real_link_list=[]
    for link in link_list:
        pic_id = link.split("/")[-1]
        real_link = "http://tiebapic.baidu.com/forum/pic/item/" + pic_id
        real_link_list.append(real_link)
    return real_link_list


def main(ID):
    link_list = []
    seelz = input("只看楼主？是的话回车：")
    if not seelz:
        url = "https://tieba.baidu.com/p/" + str(ID) + "?see_lz=1"
    else:
        url = "https://tieba.baidu.com/p/" + str(ID)
    html = getHTTPtext(url)
    alist = []
    get_information(html, link_list, alist)
    title, max_page, ba_name = alist[0], int(alist[1]), alist[2]
    try:
        for pn in range(2, max_page + 1):
            if not seelz:
                url = "https://tieba.baidu.com/p/" + str(ID) + "?see_lz=1&pn=" + str(pn)
            else:
                url = "https://tieba.baidu.com/p/" + str(ID) + "?pn=" + str(pn)
            html = getHTTPtext(url)
            add_link_list(html, link_list)
    except:
        pass
    real_link_list = real_link(link_list)
    final_list = []
    for i in range(len(real_link_list)):
        final_list.append([i + 1, real_link_list[i]])
    path_now = make_path(ba_name, title)
    len_link = len(final_list)
    for count, link in final_list:
        download_pic(link, count, path_now, len_link)


real_count = count = 0
luck = random.randint(0, 20)
while True:
    if count == 0:
        ID = int(input("输入要爬取帖子的id:"))
        main(ID)
        real_count += 1
        choose = int(input('''是否退出？
1.是
2.否
选择：'''))
        if choose == 1:
            count += 1
        elif choose == 2:
            continue
        else:
            print("？")
            time.sleep(1)
            print("emmmm")
            time.sleep(1)
            print("好吧")
            time.sleep(1)
            break
    if count == 1:
        print("感谢您的使用,本次共爬取了{}次".format(real_count))
        time.sleep(1)
        if luck == 0:
            print("注意身体")
            time.sleep(1)
        time.sleep(1)
        break
