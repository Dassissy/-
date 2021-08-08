import requests, os, re, time, random
from bs4 import BeautifulSoup
from 爬图片 import all_bar


def get_link_list(url):
    # 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    headers = {
    'Connection': 'keep-alive',
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
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    r.encoding = 'utf-8'  # 拿到源码
    tie_list = []
    tie_pages_link_list = []
    last_page_s = re.findall("<.*?>尾页<.*?>", r.text)[0]
    last_pages_num = int(re.findall(r"pn=\d+", last_page_s)[0][3:])
    pages = int(last_pages_num//50)
    begin = input("从何处开始:")
    if not begin:  # 如果直接按回车
        begin = 0
    else:
        begin = int(begin)
    for i in range(begin, pages+1):
        tie_pages_link_list.append(url+"&ie=utf-8&pn="+str(50*i))
        if (i - begin + 1) % 1 == 0:
            choose = input("已有{}个帖子，够了吗？（回车）:".format(50*(i-begin+1)))
            if not choose:  # 如果按下的是回车
                break  # 停止
    for page_link in tie_pages_link_list:
        r = requests.get(page_link, timeout=30)
        time.sleep(1)
        r.raise_for_status()
        r.encoding = 'utf-8'  # 拿到源码
        soup = BeautifulSoup(r.text, "html.parser")
        tie_list.extend(soup.find_all(href=re.compile(r"^/p/\d+")))  # 找到所有帖子的链接并并入tie_list中
    link_list = []
    for tie in tie_list:
        link_list.append(tie.attrs["href"][3:])

    return link_list


class Bar:
    def __init__(self, bar_name):
        self.name = bar_name
        self.link = "https://tieba.baidu.com/f?kw=" + bar_name
        self.link_list = get_link_list(self.link)

    def begin(self):
        pic_count = 0
        for i in range(len(self.link_list)):
            try:
                pic_count += all_bar(self.link_list[i])
            except:
                print("出错")
            print("\r本次共爬取{}/{}个帖子，已保存了{}张图片".format(i+1, len(self.link_list), pic_count))


def main():
    bar_name = input("吧名：")
    bar = Bar(bar_name)
    bar.begin()


main()