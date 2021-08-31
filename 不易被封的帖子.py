# -*- coding: utf-8 -*-
"""
爬取百度贴吧中指定帖子中的所有图片——————requests-bs4-re路线
1.0,2.0,2.5,2.6,3.0,3.2
3.5
"""
import requests, os, re, time, random
from bs4 import BeautifulSoup
import threading


def getHTTPtext(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text


def get_information(html, alist):
    first_soup = BeautifulSoup(html, "html.parser")
    r2 = re.findall(r'<title>.*?_百度贴吧', html[:5000])  # FIXME 这个html[:5000]太傻了
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
    return first_soup


def download_pic(link, count, path_now, pn, max_page):
    path = path_now + str(count) + ".png"
    try:
        if not os.path.exists(path):
            r = requests.get(link, timeout=30)
            with open(path, 'wb') as f:
                f.write(r.content)
                f.close()
                print("\r保存成功,这是第{}张图片,现在是第{}/{}页".format(count, pn, max_page), end='')
        else:
            print("文件已存在")
    except:
        print("保存失败")


def make_path(ba_name, title):
    a = input("文件路径是否使用默认设置?若否，输入从何处开始更改(从1开始)：")
    path_list = ['D', 'tieba_pics', ba_name, title[:15]]  # FIXME 吧名中可能出现“/”干扰此模块
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


def get_http_text(url):
    """多线程特供"""
    # 全程对 next_soup 上锁
    global next_soup
    threadLock.acquire()
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
    except:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
    next_html = r.text
    next_soup = BeautifulSoup(next_html, "html.parser")
    threadLock.release()
    # print("get线程结束")


def get_hrefs(max_page, seelz, first_soup):
    """一个生成器，可以次序输出一个帖子里所有图片的链接"""
    global threadLock
    p_num = 0  # 爬取的图片数
    threadLock = threading.Lock()
    
    if max_page == 1:
        first_list = first_soup("img", "BDE_Image")
        print("\r保存成功,这是第{}张图片,现在是第1/1页".format(p_num), end='')  # 跳页时也要输出一次
        for i in first_list:
            href = i.attrs['src']
            pic_id = href.split("/")[-1]
            real_href = "http://tiebapic.baidu.com/forum/pic/item/" + pic_id
            p_num += 1
            yield [p_num, 1, real_href]

    else:
        for pn in range(2, max_page + 1 + 1):
            # 这个函数的结构较为特殊，因为第一页的内容已经爬取过了，所以这里从第二页开始循环 
            # 但是是在对前一页的链接进行保存，同时利用多线程爬取这一页的内容
            # 所以在循环体中体现的就是从 2 到 max_page + 1 的一个过程

            # 爬取到第一页时，还没有下一页的内容
            if not pn == 2:
                first_soup = next_soup
            if not seelz:
                url = "https://tieba.baidu.com/p/" + str(ID) + "?see_lz=1&pn=" + str(pn)
            else:
                url = "https://tieba.baidu.com/p/" + str(ID) + "?pn=" + str(pn)
            
            # 爬取到最后一页时，不再准备下一页的内容
            if not pn == max_page + 1:
                get_next_html = threading.Thread(target=get_http_text(url))
                get_next_html.start()

            first_list = first_soup("img", "BDE_Image")
            # 跳页时需要输出一次
            print("\r保存成功,这是第{}张图片,现在是第{}/{}页".format(p_num, pn-1, max_page), end='')

            for i in first_list:
                href = i.attrs['src']
                pic_id = href.split("/")[-1]
                real_href = "http://tiebapic.baidu.com/forum/pic/item/" + pic_id
                p_num += 1
                yield [p_num, pn-1, real_href]
            


def main(ID):
    # 获取这个帖子的信息
    seelz = input("只看楼主？是的话回车：")
    if not seelz:
        url = "https://tieba.baidu.com/p/" + str(ID) + "?see_lz=1"
    else:
        url = "https://tieba.baidu.com/p/" + str(ID)
    first_html = getHTTPtext(url)
    alist = []
    first_soup = get_information(first_html, alist)
    title, max_page, ba_name = alist[0], int(alist[1]), alist[2]
    # 创建图片保存路径
    path_now = make_path(ba_name, title)
    # 开始爬取
    for p_num, pn, real_href in get_hrefs(max_page, seelz, first_soup):
        # 每次下载时都要输出
        download_pic(real_href, p_num, path_now, pn, max_page)
    

real_count = count = 0
luck = random.randint(0, 20)
while True:
    if count == 0:
        ID = int(input("输入要爬取帖子的id:"))
        main(ID)
        real_count += 1
        choose = input('''是否退出？
1.是
2.否
选择：''')
        if choose == "1":
            count += 1
        elif choose == "2":
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

