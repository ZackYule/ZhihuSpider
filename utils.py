import sys
import os
import csv
import json
from loguru import logger
from settings import *

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)

def safe_get_field_from_element(element, selector, attribute_name=""):
    try:
        if attribute_name:
            return element.query_selector(selector).get_attribute(attribute_name)
        else:
            return element.query_selector(selector).inner_text()
    except:
        logger.warning('target value not obtained, relevant information:'+selector+attribute_name)
        return " "

def csv_pipeline(item:dict, keyword:str, content_type:str, header:list[str]):
    base_dir = '结果文件' + os.sep + keyword
    file_path = base_dir + os.sep + keyword + content_type + '.csv'

    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
    if not os.path.isfile(file_path):
        is_first_write = 1
    else:
        is_first_write = 0
        
    if item:
        with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if is_first_write:
                if header:
                    writer.writerow(header)
            writer.writerow([item[key] for key in item.keys()])

def get_content_info_from_csv(title:str)->list[dict]:
    base_dir = '结果文件' + os.sep + title
    file_path = base_dir + os.sep + title +'问题链接' + '.csv'

    if not (os.path.isdir(base_dir) |  os.path.isfile(file_path)):
        return []
    
    items = []
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items

def login(p, url):
    browser = p.webkit.launch(headless=HEAD_V, slow_mo = SLOW_MO_V)
    if os.path.isfile("state_zhihu.json"):
        with open("state_zhihu.json") as f:
            storage_state = json.loads(f.read())
        context = browser.new_context(viewport={ 'width': 1440, 'height': 860 },storage_state=storage_state)
        page = context.new_page()
        page.goto(url)
        logger.info("免认证登录成功")
    else:
        logger.info("免认证登录失败，请打开切换开发环境(ENV=DEV)手动验证...自动验证太难了555...")
        context = browser.new_context(viewport={ 'width': 1440, 'height': 860 })
        page = context.new_page()
         # Go to https://www.zhihu.com/signin?next=%2Fhot
        page.goto("https://www.zhihu.com/signin?next=%2Fhot")
        # Click text=密码登录
        page.locator("text=密码登录").click()
        # Click [placeholder="手机号或邮箱"]
        page.locator("[placeholder=\"手机号或邮箱\"]").type(ACCOUNT)
        # Click [placeholder="密码"]
        page.locator("[placeholder=\"密码\"]").type(PASSWORD)
        # Click text=登录/注册
        page.locator("text=登录/注册").click()
        page.wait_for_timeout(10000)
        storage = context.storage_state()
        with open("state_zhihu.json", "w") as f:
            f.write(json.dumps(storage))
        page.goto(url)
        logger.info('登录成功！')
    return (browser, context, page)