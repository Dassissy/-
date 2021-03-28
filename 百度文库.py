# -*- coding: utf-8 -*-
"""
爬取百度文库信息
截图-图片裁剪（没做）-转文字
"""
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_title(wenku_id="02058322afaad1f34693daef5ef7ba0d4b736df2"):
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text,"html.parser")
    title = soup.find('title').string
    title = title.split(' ')[0]
    return title

driver = webdriver.Chrome()

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
    page_height = 730
    times = height//page_height
    js_0 = "var q=document.documentElement.scrollTop=" + str(height//2)#下拉引出奇怪东西
    driver.execute_script(js_0)
    time.sleep(1.5)
    driver.find_element_by_xpath(r"//div[@class='vip-pop-wrap inner-vip'][1]/span").click()#关掉
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
    
def initialize_changeTOtext():#初始化图片转文字
    url = "http://www.imagetotxt.com/"
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
    print(str(error_dict))

def error_handling(error_dict,html_dict):
    time.sleep(2)
    if error_dict:#如果字典非空
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
        error_handling(error_dict, html_dict)#递归直至解决所有问题         
    else:
        driver.quit()#退出循环

def main():
    title = get_title()
    get_clean_window()
    time.sleep(1)
    scr_list = []
    html_dict = {}
    error_dict = {}
    get_screenshot(scr_list,title)
    change_to_text(scr_list,html_dict,error_dict)
    error_handling(error_dict,html_dict)
    #临时代码
    string = ''
    for count in html_dict:
        string = string + html_dict[count]
    print(string)
    with open("D://测试文档//测试文本.txt","w",encoding='utf-8') as f:
        f.write(string)
        f.close()
main()