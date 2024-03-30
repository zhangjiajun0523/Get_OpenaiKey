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
    print(f"『执行』:获取手机号成功:{mobile}")
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
    print("『执行』:开始获取短信验证码...")
    while True:
        url = "http://api.sqhyw.net:90/api/get_message"
        params = {
            "token": token,
            "project_id": project_id,
            "phone_num": phone_num,
            "special": special
        }
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
            if time.time() - start_time > 60:  # 超过60秒则退出循环
                free_result = free_phone(project_id, special, token, phone_num)
                print("『执行』:获取接码平台手机号上的验证码失败, 超过60秒未获取到验证码," + free_result)
                time.sleep(5)
                break  # 跳出当前循环，重新获取新的手机号
        time.sleep(5)  # 每隔5秒尝试一次


# 直接导入oneapi
def add_key(refresh_token):
    url = "https://api.oxvip.cn/api/channel/?p=0"
    logging.info(url)
    refresh_tokens = refresh_token[-25:]
    # 创建JSON对象
    jsonObject = {
        "type": 25,
        "key": refresh_token,
        "name": f"Moonshot AI〖{refresh_tokens}〗",
        "base_url": "http://154.9.30.247:8099",
        "other": f"{refresh_token}",
        "models": "kimi,moonshot-v1-8k,moonshot-v1-32k,moonshot-v1-128k",
        "group": "default,vip,svip",
        "model_mapping": "Moonshot AI",
        "priority": 15,
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
        print(response_content)
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
    "free_1": 'https://kimi.moonshot.cn/',
}


def GetTime():
    now = datetime.datetime.now()
    millisecond = int(now.microsecond / 1000)
    time_str = now.strftime("%Y-%m-%d %H:%M:%S") + f".{millisecond:03}"
    return time_str


def update_token_in_file2(filename, serial_number, new_token, phone_num, state):
    # 确保文件存在，如果不存在则创建
    if not os.path.isfile(filename):
        open(filename, 'a').close()
    # 读取原始文件内容
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 找到需要更新的行
    updated = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(serial_number):
            # 在找到的行中添加新的 refresh_token 和 phone_num, state
            updated_line = f"{line.strip()};{new_token};{phone_num};{state}\n"
            new_lines.append(updated_line)
            updated = True
        else:
            new_lines.append(line)

    # 如果没有找到对应的行，可以添加新的内容
    if not updated:
        new_lines.append(f"{serial_number};{new_token};{phone_num};{state}\n")

    # 将更新后的内容写回文件
    with open(filename, 'w') as f:
        f.writelines(new_lines)

def update_token_in_file(filename, new_token, phone_num, state):
    # 确保文件存在，如果不存在则创建
    if not os.path.isfile(filename):
        open(filename, 'a').close()

    # 直接在文件末尾添加新的内容
    with open(filename, 'a') as f:
        f.write(f"{new_token};{phone_num};{state}\n")

def get_token(Serial_number):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')  # 启用无头模式
    options.add_argument('--disable-gpu')  # 禁用图形硬件加速
    options.add_argument('--no-sandbox')  # 在沙盒模式下运行
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
    driver = webdriver.Chrome()

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
    # time.sleep(5)
    # # 找到登录按钮的 XPath
    # login_button_xpath = "/html/body/div/div/div[2]/div[2]/div/div[1]/div/div/div"
    # driver.find_element(By.XPATH, login_button_xpath).click()
    # 找到登录按钮的 XPath
    login_button_xpath = "/html/body/div/div/div[2]/div[2]/div/div[1]/div/div/div"
    # 设置最多等待时间，例如10秒
    wait = WebDriverWait(driver, 10)
    # 等待直到登录按钮出现
    login_button = wait.until(EC.visibility_of_element_located((By.XPATH, login_button_xpath)))
    # 找到登录按钮并点击它
    # driver.find_element(By.XPATH, login_button_xpath).click()
    login_button.click()

    # 获取接码平台手机号
    username = "zhangjiajun"
    password = "0sea.o5.23"
    token = get_phone_token(username, password)
    project_id = "763005----4G62SD"
    special = 1
    phone_num = get_phone(project_id, special, token)
    print(
        f"『执行』:当前登录地址=地址为:〖{selected_url}〗,当前登录账号为:〖{phone_num}〗，获取refresh_token运行中~ ----{GetTime()}")
    # 输入接码平台手机号
    driver.find_element(By.XPATH, "//*[@id='phone']").send_keys(phone_num)
    # 找到验证码按钮的 XPath并点击他获取验证码
    MuiButton_xpath = "/html/body/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[1]/div[1]/div[3]/div[2]/button/span[1]"
    driver.find_element(By.XPATH, MuiButton_xpath).click()
    # time.sleep(10)
    phone_Code = get_phone_code(project_id, special, phone_num, token)
    if phone_Code:
        print(f"『执行』:成功获取手机号{phone_num}上的验证码:{phone_Code}")
    else:
        print("『执行』:未能获取手机号{phone_num}上的验证码，继续尝试。")
    # 输入获取到的验证码,即可登录成功
    driver.find_element(By.XPATH, "//*[@id='verify_code']").send_keys(phone_Code)
    # 找到最终登录按钮的 XPath并点击他获取验证码
    # SubmitButton_xpath = "/html/body/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[1]/div[1]/button/span"
    # driver.find_element(By.XPATH, SubmitButton_xpath).click()
    # driver.find_element(By.XPATH, "//button[@id=':rq:']").click()
    # 找到文本框元素的 XPath
    time.sleep(3)
    text_box_xpath = "/html/body/div/div/div[2]/div[3]/div/div[2]/div/div[3]/div[1]/div/div/div[1]/div"
    # 在这个文本框里输入“你好！”
    driver.find_element(By.XPATH, text_box_xpath).send_keys("你好！")
    # driver.send_keys(Keys.RETURN)
    # 找到验证码按钮的 XPath并点击他获取验证码
    send_button_xpath = "/html/body/div/div/div[2]/div[3]/div/div[2]/div/div[3]/div[1]/div/div/div[2]/div[3]/button/span[1]"
    driver.find_element(By.XPATH, send_button_xpath).click()
    # 使用 execute_script 方法执行 JavaScript 代码来获取 Local Storage 中的 refresh_token
    refresh_token = driver.execute_script("return localStorage.getItem('refresh_token');")
    # 打印获取到的 refresh_token 值
    # print("获取到的 refresh_token 值为:", refresh_token)
    print(
        f"『执行』:当前登录地址地址为:〖{selected_url}〗,当前登录账号为:〖{phone_num}〗，获取refresh_token成功:{refresh_token} ----{GetTime()}")
    # 获取完refresh_token直接导入oneapi渠道中
    State = True
    add_key(refresh_token)
    # 写入账号txt中
    reten = update_token_in_file("get_token_key_add.txt",refresh_token, phone_num, State)
    # reten = update_token_in_file("get_token_key_add.txt", f"{Serial_number};{State}", refresh_token, phone_num, State)
    driver.quit()
    # print("✿✿ヽ(°▽°)ノ✿撒花~~~获取零一AI-key任务Over!")
    return "『执行』:✿✿ヽ(°▽°)ノ✿撒花~~~获取Kimi-AI-refresh_token任务Over!"


def get_token_multi_thread2(Get_token):
    Serial_number, State = Get_token.split(';')
    return get_token(Serial_number)


def get_token_multi_thread(Get_token):
    # 使用 split(';') 分割字符串，并将结果存储在一个列表中
    tokens = Get_token.split(';')

    # 检查分割后的结果数量
    if len(tokens) >= 2:
        # 如果结果有两个或更多，按照预期赋值给 Serial_number 和 State
        Serial_number, State = tokens[0], tokens[1]
    else:
        # 如果结果少于两个，抛出一个异常或者进行其他的错误处理
        raise ValueError("『执行』:Get_token string does not contain at least two values separated by semicolon.")

    # 调用 get_token 函数，并传入 Serial_number 作为参数
    return get_token(Serial_number)


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
