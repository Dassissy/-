# -*- coding: utf-8 -*-
"""
爬取百度文库信息
截图-图片裁剪-转文字

!去重部分仍有问题，可能为:较短的句子易被误删
"""
import requests
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

def get_info(wenku_id="02058322afaad1f34693daef5ef7ba0d4b736df2"):#拿到一些信息
    url = "https://wenku.baidu.com/view/" + wenku_id + ".html"
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text,"html.parser")
    title = soup.find('title').string
    title = title.split(' ')[0]
    dividers = soup.find_all("span",attrs={'class':'divider'})
    divider = dividers[-1]
    num_of_pages = divider.find_next().string[:-1]
    return title,num_of_pages

def get_clean_window(num_of_pages,wenku_id="02058322afaad1f34693daef5ef7ba0d4b736df2"):#登录百度文库
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
    remove_list = ["//div[@class='header-wrapper no-full-screen new-header']",
                   "//div[@class='left-wrapper zoom-scale']/div[@class='no-full-screen']",
                   "//div[@class='reader-wrap']/div/div[@class='reader-topbar']",
                   "//div[@class='right-wrapper no-full-screen']",
                   "//div[@class='color-plate']",
                   "//div[@class='lazy-load']/div[@class='sidebar-wrapper']",
                   "//div[@class='try-end-fold-page']"]#除广告及水印外所有需删除的元素
    for ele_path in remove_list:
        ele = driver.find_element(By.XPATH,ele_path)
        driver.execute_script("""var element = arguments[0];
                              element.parentNode.removeChild(element)""",ele)#第一句是在传入ele，第二句执行删除
    hx_warp_x_path = "//div[@class='hx-warp']"#接下来对广告下手
    hx_warps = driver.find_elements(By.XPATH,hx_warp_x_path)
    for hx in hx_warps:
        driver.execute_script("""var element = arguments[0];
                              element.parentNode.removeChild(element)""",hx)
#问题：水印可以被定位，但无法被删除
"""
    _wmlist = []#现在去水印
    for i in range(int(num_of_pages)):
        _wmlist.append("__wm"+str(i+1))
    for _wm in _wmlist:
        _wm_x_path = r"//div[@class='" + _wm + r"']"
        wm = driver.find_element(By.XPATH,_wm_x_path)
        driver.execute_script('''var element = arguments[0];
                              element.parentNode.removeChild(element)''',wm)
                              """
    #还有一个小东西放到下一个函数去关掉
        
def get_screenshot(scr_list,title = ' '):
    height = driver.find_element(By.TAG_NAME,"body").size["height"]
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
  
def judge(img):#判断图片是否完整 
    threshold = 210#定义灰度界限
    table = []
    for i in range(256):
      if i < threshold:
        table.append(0)
      else:
        table.append(1)
        
    img = img.convert('L')
    bw_img = img.point(table, '1')#图片二值化
    
    size = bw_img.size
    #print(("size is:{}").format(size))
    w = size[0]
    bw_img_list = bw_img.load()#获取像素点列表
    black = 0
    white = 0
    for i in range(w):
        data = bw_img_list[i,0]
        #print(("data is:{}").format(data))
        if data == 0:
            black += 1
        else:
            white += 1
    #print(("black is:{}, white is:{}").format(black, white))
    if black == 0:
        return True#图片完整
    else:
        return False#图片不完整
    
def crop_pictures(scr_list):
    """
    不需要截取了
    count = 0
    for path in scr_list:
        im = Image.open(path)
        if count == 0:
            cropped_image = im.crop((448,457,1150,900))#第一张自然不一样
            count += 1
        else:
            cropped_image = im.crop((448,113,1150,830))#吃的是元组所以套两层括号哦
        cropped_image.save(path)
        """
    for path in scr_list:
        #print(("现在是{}").format(path))
        im = Image.open(path)
        #print(("im.size is:{}").format(im.size))
        l,w = im.size
        for i in range(w):#自上而下遍历图片的每一列
            box = (0,i,l,i+1)#左上右下
            IM = im.crop(box)
            judgement = judge(IM)
            if judgement == True:
                if i != 0:
                    new_box = (0,i,l,w)
                    im = im.crop(new_box)
                    #print(("this part worked"))
                break
            else:
                continue
        im = im.rotate(180)#翻转
        l,w = im.size#图片大小可能出现变化
        for i in range(w):#自上而下遍历图片的每一列
            box = (0,i,l,i+1)#左上右下
            IM = im.crop(box)
            judgement = judge(IM)
            if judgement == True:
                if i != 0:
                    new_box = (0,i,l,w)
                    im = im.crop(new_box)
                    #print(("this part worked,too"))
                break
            else:
                continue
        im = im.rotate(180)#转回来
        im.save(path)
           
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
    title,num_of_pages = get_info()#首先拿到标题和总页数
    get_clean_window(num_of_pages=num_of_pages)#把窗口的各种影响阅读的弹窗清一遍
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

