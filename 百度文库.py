# -*- coding: utf-8 -*-
"""
爬取百度文库信息
截图-图片裁剪-转文字

！！转文字多次再去重不可行，反而会使输出更加混乱
"""
import requests#发送请求较快,用于拿到文章标题
from bs4 import BeautifulSoup#提取网页中需要的内容
import re
import time
#走网页前端,故使用selenium库
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os#文件操作
from PIL import Image#图片操作
from fuzzywuzzy import fuzz#相似度判定

def get_title(wenku_id="02058322afaad1f34693daef5ef7ba0d4b736df2"):
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text,"html.parser")
    title = soup.find('title').string
    title = title.split(' ')[0]
    return title

def get_clean_window(wenku_id="02058322afaad1f34693daef5ef7ba0d4b736df2"):#登录百度文库
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    with open(r'D:\python\wenku_cookie.txt','r') as f:
        cookie_string = f.read()
        cookie_string = re.sub("true","True",cookie_string)
        cookie_string = re.sub("false","False",cookie_string)
        cookie_list = list(eval(cookie_string))
    driver.get(url)
    for cookie in cookie_list:
        if cookie['sameSite']:
            cookie.pop('sameSite')
        driver.add_cookie(cookie)
    driver.get(url)#打开页面
    time.sleep(3)
    card = driver.find_element(By.CLASS_NAME,"experience-card-content")#弹出奇怪的东西
    close = card.find_element(By.CLASS_NAME,"close-btn")
    close.click()#关掉
    time.sleep(1)
    read_all = driver.find_element(By.CLASS_NAME,"read-all")#展开
    driver.execute_script("arguments[0].click();", read_all)#聚焦并点击
    #还有一个小东西放到下一个函数去关掉
        
def get_screenshot(scr_list,title = ' '):
    height = driver.find_element_by_tag_name("body").size["height"]
    page_height = 670#实际为730,截多一点
    times = height//page_height
    js_0 = "var q=document.documentElement.scrollTop=" + str(height//2)#下拉引出奇怪东西
    driver.execute_script(js_0)
    time.sleep(1.5)
    driver.find_element(By.XPATH,r"//div[@class='vip-pop-wrap inner-vip'][1]/span").click()#关掉
    driver.execute_script("var q=document.documentElement.scrollTop=0")#回到顶部
    driver.maximize_window()#全屏显示
    time.sleep(1)
    for i in range(times):
        js = "var q=document.documentElement.scrollTop=" + str(i*page_height)
        driver.execute_script(js)
        scr_path = "D://wenku_pics//" + title + "//"
        if not os.path.exists(scr_path):
            os.mkdir(scr_path)
        scr_name = scr_path + str(i+1) + ".png"
        scr_list.append(scr_name)
        driver.save_screenshot(scr_name)
        time.sleep(0.1)
    #删除后三张图
    for i in range(2):#如此往复3次
        path = scr_list[-1]#最后一张图被删除
        os.remove(path)
        scr_list.pop(-1)#最后一张图被弹出
        
def crop_pictures(scr_list):
    count = 0
    for path in scr_list:
        im = Image.open(path)
        if count == 0:
            cropped_image = im.crop((448,457,1150,915))#第一张自然不一样
            count += 1
        else:
            cropped_image = im.crop((448,113,1150,870))#吃的是元组所以套两层括号哦
        cropped_image.save(path)
           
def initialize_changeTOtext():#初始化图片转文字
    url = "http://www.imagetotxt.com/"
    try:
        driver.get(url)
    except:#这服务器好差
        time.sleep(60)
        driver.get(url)
    choose = driver.find_element(By.ID,"ddlLanguage")#语言改为英语
    choose.click()
    chooses = choose.find_elements(By.TAG_NAME,"option")
    eng = chooses[2]
    eng.click()
    time.sleep(2)
    choose.click()#关闭语言选择窗

def change_to_text(scr_list,html_dict,error_dict):
    initialize_changeTOtext()
    original_handle = driver.current_window_handle
    times = 1
    for path in scr_list:
        time.sleep(2)
        choose_file = driver.find_element(By.CLASS_NAME,"newFile")
        choose_file.send_keys(path)#传入路径
        time.sleep(0.3)
        driver.find_element(By.ID,"cmdSaveAttachment").click()#开始转文字
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT,"下载文件"))).click()
        except:
            time.sleep(20)
            error_dict[str(times)] = path
            times += 1#times的值加上1以保证能与continue后的path对应
            initialize_changeTOtext()#初始化
            original_handle = driver.current_window_handle
            continue
        WebDriverWait(driver,5).until(EC.number_of_windows_to_be(2))#转到另一个窗口
        for handle in driver.window_handles:
            if handle != original_handle:
                driver.switch_to.window(handle)
                break
        time.sleep(1.5)
        html = driver.execute_script("return document.documentElement.outerHTML")#拿到源码
        html_dict[str(times)] = html#往字典里加东西
        driver.close()#关闭窗口
        driver.switch_to.window(original_handle)#聚焦原窗口
        times += 1

def error_handling(error_dict,html_dict,PASS=0):#PASS的触发：某些图片总是出错（两次以上）
    time.sleep(2)
    if error_dict and PASS <= 2:#如果字典非空,且未触发PASS
        print(str(error_dict))#写一下错误字典
        initialize_changeTOtext()#重开转文字网站
        original_handle = driver.current_window_handle#拿到窗口句柄方便之后聚焦
        error_list = []
        for _time_ in error_dict:
            error_path = error_dict[_time_]
            choose_file = driver.find_element(By.CLASS_NAME,"newFile")
            choose_file.send_keys(error_path)#传入路径
            time.sleep(0.3)
            driver.find_element(By.ID,"cmdSaveAttachment").click()#转文字
            try:
                WebDriverWait(driver,30).until(EC.presence_of_element_located((By.LINK_TEXT,"下载文件"))).click()
            except:
                time.sleep(30)#再等半分钟
                continue
            WebDriverWait(driver,5).until(EC.number_of_windows_to_be(2))#转到另一个窗口
            for handle in driver.window_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    break
            time.sleep(1.5)
            html = driver.execute_script("return document.documentElement.outerHTML")#拿到源码
            html_dict[str(_time_)] = html#往字典里加东西
            error_list.append(str(_time_))#输入没出错的序号，不能在循环内部直接删除字典中的内容
            driver.close()#关闭窗口
            driver.switch_to.window(original_handle)#聚焦原窗口
        for i in error_list:
            del error_dict[i]
        if not error_list:#若错误无法解决
            PASS += 1
        error_handling(error_dict, html_dict ,PASS)#递归直至解决所有问题         
    else:
        driver.quit()#递归出口,关闭浏览器
        
def out(html_dict):
    key_list = list(html_dict.keys())
    key_list.sort()#排序
    out_string = ''
    for key in key_list:
        soup = BeautifulSoup(html_dict[key],"html.parser")
        string = soup.find("pre").string#提取文字部分
        out_string = out_string + string
    lines = out_string.split("\n")
    out_string = ''
    duplicate_removal(lines)#去重
    for line in lines:
        out_string = out_string + line + "\n"#把空格补回来
    with open("D://阅读//测试文本4.txt","w",encoding='utf-8') as f:
        f.write(out_string)
        f.close()
        
def duplicate_removal(lines,count = 0):#去重
    line = lines[count]#每次仅取一句进行查重
    index_list = []
    index = count + 1#不要和自己查重
    duplicate_list = []#重复的放到一个列表里头
    for l in lines[index:]:
        if fuzz.ratio(line,l) >= 80:#相似度>=80就判定为一致
            index_list.append(lines.index(l))
    for i in index_list:
        duplicate_list.append(lines[i])
        lines.pop(i)
    duplicate_list.append(lines[count])#把用于匹配的字符串放入重复列表中
    if len(duplicate_list) >= 4:#多次重复则是真的重复
        pass
    else:
        lines[count] = duplicate_list[-1]#重复数为1或2则取后一个  
    count += 1
    if count == len(lines):#递归出口，运行到底时退出
        pass
    else:
        duplicate_removal(lines,count)#下一层递归

def main():
    title = get_title()#首先拿到标题
    get_clean_window()#把窗口的各种影响阅读的弹窗清一遍
    time.sleep(1)
    scr_list = []
    html_dict = {}
    error_dict = {}#字典不能连续赋值
    get_screenshot(scr_list,title)#屏幕截图
    crop_pictures(scr_list)#将不必要的部分裁去
    change_to_text(scr_list,html_dict,error_dict)#图片转文字
    error_handling(error_dict,html_dict)#转文字网站服务器容易崩,所以搞一个错误处理
    out(html_dict)#输出成文档
   
driver = webdriver.Chrome()#用谷歌,只能用谷歌,用火狐的话要改好多
main()