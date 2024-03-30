from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support import expected_conditions as EC
import datetime
import time
import json
import requests
import os
import random  # 新增随机模块
from concurrent.futures import ThreadPoolExecutor
import configparser
from seleniumwire import webdriver  # 代理IP
import logging


# 获取接码平台token
def get_phone_token(username, password):
    url = "http://api.sqhyw.net:90/api/logins"
    params = {
        "username": username,
        "password": password
    }
    # response = requests.get(url, params=params)
    # data = response.json()
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(f'『执行』:监听获取接码Token状态正常!状态码: 〖{response.status_code}〗')
            # 继续执行后面的代码
            # response = requests.get(url, params=params)
            break
        else:
            print(f"『执行』:监听获取接码Token状态异常!状态码: {response.status_code}，等待1秒后重试...")
            time.sleep(1)
            response = requests.get(url, params=params)

    data = response.json()
    token = data["token"]
    return token


# 获取kimiai接码手机号
def get_phone(project_id, special, token):
    url = "http://api.sqhyw.net:90/api/get_mobile"
    params = {
        "token": token,
        "project_id": project_id,
        "special": special
    }
    # response = requests.get(url, params=params)
    # data = response.json()
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(f'『执行』:监听获取手机号状态正常!状态码: 〖{response.status_code}〗')
            # 继续执行后面的代码
            # response = requests.get(url, params=params)
            break
        else:
            print(f"『执行』:监听获取手机号状态异常!状态码: {response.status_code}，等待1秒后重试...")
            time.sleep(1)
            response = requests.get(url, params=params)

    data = response.json()
    mobile = data.get("mobile", None)
    print(f"获取手机号成功:{mobile}")
    return mobile


# 释放接码手机号
def free_phone(project_id, special, token, phone_num):
    url = "http://api.sqhyw.net:90/api/free_mobile"
    params = {
        "token": token,
        "project_id": project_id,
        "special": special,
        "phone_num": phone_num,
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data["message"] == "ok":
        return f'释放手机{phone_num}号成功!'
    else:
        return f'释放手机{phone_num}号失败!原因为:' + data["message"]


# 获取kimiai接码手机号上的验证码
def get_phone_code(project_id, special, phone_num, token):
    start_time = time.time()  # 记录开始时间
    print("『执行』:开始获取验证码...")
    while True:
        url = "http://api.sqhyw.net:90/api/get_message"
        params = {
            "token": token,
            "project_id": project_id,
            "phone_num": phone_num,
            "special": special
        }
        # response = requests.get(url, params=params)
        # data = response.json()
        while True:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print(f'『执行』:监听获取短信验证码状态正常!状态码: 〖{response.status_code}〗')
                # 继续执行后面的代码
                # response = requests.get(url, params=params)
                break
            else:
                print(f"『执行』:监听获取短信验证码状态异常!状态码: {response.status_code}，等待1秒后重试...")
                time.sleep(1)
                response = requests.get(url, params=params)

        data = response.json()
        print(f'『执行』:监听获取短信验证码Message:〖' + data["message"] + '〗')
        if data["message"] == "ok":
            phone_Code = data["code"]
            # print("获取接码平台手机号上的验证码成功:" + phone_Code)
            return phone_Code  # 返回获取到的验证码
        else:
            print("『执行』:等待验证码中，请耐心等待...")
            if time.time() - start_time > 60:  # 超过10秒则退出循环
                free_result = free_phone(project_id, special, token, phone_num)
                print("『执行』:获取接码平台手机号上的验证码失败, 超过20秒未获取到验证码," + free_result)
                time.sleep(10)
                break  # 跳出当前循环，重新获取新的手机号
        time.sleep(5)  # 每隔5秒尝试一次


# 直接导入oneapi
def add_key(keys):
    url = "https://api.oxvip.cn/api/channel/?p=0"
    logging.info(url)

    # 创建JSON对象
    jsonObject = {
        "type": 31,
        "key": keys,
        "name": f"零一AI〖{keys}〗",
        "base_url": "https://api.lingyiwanwu.com",
        "other": "零一万物",
        "models": "yi-34b-chat-0205,yi-vl-plus,yi-34b-chat-200k",
        "group": "default,vip,svip",
        "model_mapping": "零一万物",
        "priority": 16,
        # "groups": "gpt-4"
    }

    # 将JSON对象转换为字符串
    json_data = json.dumps(jsonObject)

    # 发送HTTP POST请求
    try:
        response = requests.post(url, headers={
            "Authorization": "Bearer " + "bab17ea55d11428cada2f8a1e23f097a",
            "Content-Type": "application/json; charset=utf-8"
        }, data=json_data)

        # 检查响应状态
        if response.status_code != 200:
            logging.info(f"『执行』:请求one-api失败，失败码: {response.status_code}")
            return False

        # 解析响应内容
        response_content = response.json()
        # print(response_content)
        success = response_content.get("success", False)
        print(f"『执行』:添加OneAPI渠道执行状态：{success}，恭喜！OneAPI渠道添加成功！")
        if success:
            return True

        else:
            logging.info(f"『执行』:请求one-api失败，失败码: {response.status_code}")
    except Exception as e:
        logging.error("『执行』:请求one-api时发生错误: %s", str(e))

    return False


# 读取配置文件中需要打开的标签数
def get_config_number_labels(config_file_path='config.ini'):
    try:
        # 获取当前脚本所在目录，并构建配置文件的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_file_path)

        # 实例化 ConfigParser 对象
        config = configparser.ConfigParser()

        # 读取配置文件
        config.read(config_path, encoding='GB18030')

        # 获取配置项值，提供默认值为 1
        return int(config.get('config', 'number_labels', fallback=0))

    except (configparser.Error, ValueError) as e:
        # 处理配置文件读取或解析错误，或者转换为整数时的错误
        print(f"Error reading configuration: {e}")
        return 1


# 定义一个字典，包含多个接口地址
url_dict = {
    "free_1": 'https://platform.lingyiwanwu.com/apikeys',
}


def GetTime():
    now = datetime.datetime.now()
    millisecond = int(now.microsecond / 1000)
    time_str = now.strftime("%Y-%m-%d %H:%M:%S") + f".{millisecond:03}"
    return time_str


def update_token_in_file(filename, line_to_update, new_token):
    lines = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            lines.append(line.strip())

    for i, line in enumerate(lines):
        if line.startswith(line_to_update):
            lines[i] = f"{line_to_update};{new_token}"
            break

    with open(filename, 'w') as f:
        for line in lines:
            f.write(line + '\n')


def get_token(phone, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    # 代理
    wire_options = {
        'proxy': {
            'http': 'http://zhangjiajun0523:Sea19990523@geo.iproyal.com:12321',
            'https': 'http://zhangjiajun0523:Sea19990523@geo.iproyal.com:12321',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    # 代理IP访问
    # driver = webdriver.Edge(seleniumwire_options=wire_options)
    # 不使用代理IP访问
    driver = webdriver.Edge()
    time.sleep(100)

    # 单地址访问
    # url = 'https://free-1.xyhelper.cn/getsession'

    # 随机选择一个接口地址
    selected_url = random.choice(list(url_dict.values()))
    print(selected_url)
    while True:
        try:
            driver.get(selected_url)
            break
        except:
            continue
    # 获取接码平台手机号
    username = "zhangjiajun"
    password = "0sea.o5.23"
    token = get_phone_token(username, password)
    project_id = "778897----J09G74"  # 项目ID
    special = 1
    # 获取手机号-----------------------------------------------------------关键要素
    phone_num = get_phone(project_id, special, token)
    print(
        f"『执行』:当前登录地址=地址为:〖{selected_url}〗,当前登录账号为:〖{phone_num}〗，获取零一AI-key任务执行中~ ----{GetTime()}")
    # wait = WebDriverWait(driver, 25)  # 设置等待时间为5秒
    # # 定位到iframe
    # stripe_iframe = wait.until(
    #         EC.presence_of_element_located((By.XPATH, '//iframe[starts-with(@name,"__privateStripeFrame")]')))
    # driver.switch_to.frame(stripe_iframe)
    # #print("测试2")
    # # 操作iframe内部的元素
    # card_number_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="phoneCode_identify"]')))
    # card_number_input.send_keys(phone_num)

    try:
        # 以确保页面加载完毕,等待25秒
        wait = WebDriverWait(driver, 25)

        # 定位到包含目标元素的iframe，这里使用'verifyIframe'作为该iframe的类名来定位
        stripe_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.login-iframe')))

        # 切换到找到的iframe-----------------------关键要素
        driver.switch_to.frame(stripe_iframe)

        # 在iframe内部定位到目标元素，定位到手机号标签
        card_number_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="phoneCode_identify"]')))
        # 输入接码平台手机号
        card_number_input.send_keys(phone_num)

        # 定位到点击获取验证码按钮
        button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'authing-g2-send-code-btn')))
        button.click()

        # 定位复选框
        checkbox = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'authing-ant-checkbox-input')))
        checkbox.click()

        # 定位到验证码input
        card_number_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="phoneCode_code"]')))
        # 等待获取验证码中-----------------------------------------------------------关键要素
        phone_Code = get_phone_code(project_id, special, phone_num, token)
        if phone_Code:
            print(f"『执行』:成功获取手机号{phone_num}上的验证码:{phone_Code}")
        else:
            print("『执行』:未能获取手机号{phone_num}上的验证码，继续尝试。")
        # 输入验证码
        card_number_input.send_keys(phone_Code)

        # 定位到登录按钮
        button2 = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'authing-g2-submit-button')))
        # 点击按钮
        button2.click()

        # 找到获取key的A标签
        time.sleep(10)
        link = wait.until(EC.presence_of_element_located((By.XPATH,
                                                          '/html/body/div/div/main/div/div/div/div[1]/div/div/div/div/div/div/div/table/tbody/tr[1]/td[2]/a')))
        # 点击找到的链接
        link.click()

        # 定位到key
        input_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/span[2]/span/input')))
        # 获取input元素的value值
        keys = input_element.get_attribute("value")
        print(
            f"『执行』:当前登录地址地址为:〖{selected_url}〗,当前登录账号为:〖{phone_num}〗，获取零一AI-key成功:{keys} ----{GetTime()}")
        # 获取完零一AI-key直接导入oneapi渠道中
        add_key(keys)
        # 写入账号txt中
        reten = update_token_in_file(filename, f"{phone_num};{password}", keys)
    finally:
        print("『执行』:✿✿ヽ(°▽°)ノ✿撒花~~~获取零一AI-key任务Over!")
        # 执行完操作后，不要忘记退出浏览器
        driver.quit()
    return "『执行』:获取零一AI-key成功!"


def get_token_multi_thread(mail_password):
    mail, password, State = mail_password.split(';')
    return get_token(mail, password)


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    filename = os.path.join(script_dir, 'get_token_key.txt')

    lines = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            lines.append(line.strip())
    # 获取config.ini文件中设定的打开进程数
    number_labels = get_config_number_labels()
    with ThreadPoolExecutor(max_workers=number_labels) as executor:
        results = list(executor.map(get_token_multi_thread, lines))

    for result in results:
        print(result)
        # 如果需要，可以将结果写入文件或进行其他操作
        # update_token_in_file(filename, f"{mail};{password}", new_token)
