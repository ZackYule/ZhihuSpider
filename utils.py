import sys
import os
import csv
import json
from loguru import logger
from settings import *

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)


def safe_drag_list(locator_list, page):
    try:
        locator_list.last.scroll_into_view_if_needed()
        content_div_height = locator_list.last.bounding_box()['height']
        page.mouse.wheel(0, content_div_height / 2)
        # if content_div_height > 860:
        #     logger.debug('太大放不下了...')
    except Exception:
        logger.warning('最后一个块儿无法获取高度...')
        logger.warning(locator_list.last)
        logger.warning(Exception)
        page.mouse.wheel(0, 500)


def safe_get_field_from_element(element, selector, attribute_name=""):
    try:
        if attribute_name:
            return element.query_selector(selector).get_attribute(
                attribute_name)
        else:
            return element.query_selector(selector).inner_text()
    except:
        logger.warning('target value not obtained, relevant information:' +
                       selector + attribute_name)
        return " "


def safe_get_field_from_locator(locator, selector, attribute_name=""):
    try:
        if attribute_name:
            return locator.locator(selector).get_attribute(attribute_name)
        else:
            return locator.locator(selector).inner_text()
    except:
        logger.warning('target value not obtained, relevant information:' +
                       selector + attribute_name)
        return " "


def get_target_item(item_before: dict, item_model: list):
    item_after = {}
    for title in item_model:
        if title in item_before:
            item_after[title] = item_before[title]
        else:
            item_after[title] = ''
    return item_after


def csv_pipeline(item: dict, keyword: str, content_type: str,
                 header: list[str]):
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


def get_content_info_from_csv(title: str, content_type: str) -> list[dict]:
    base_dir = '结果文件' + os.sep + title
    file_path = base_dir + os.sep + title + content_type + '.csv'

    if not (os.path.isdir(base_dir) | os.path.isfile(file_path)):
        logger.info('没有找到要爬取数据的文件')
        return []

    items = []
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items


def get_column_info_info_from_csv(title: str, content_type: str,
                                  column_num: int) -> list:
    base_dir = '结果文件' + os.sep + title
    file_path = base_dir + os.sep + title + content_type + '.csv'
    logger.debug(file_path)
    if not (os.path.isdir(base_dir) | os.path.isfile(file_path)):
        logger.info('没有找到要爬取数据的文件')
        return []

    items = []
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        is_first_read = True
        for row in reader:
            if is_first_read:
                is_first_read = False
                continue
            items.append(row[column_num])
    return items


def login(p, url):
    browser = p.webkit.launch(headless=HEAD_V, slow_mo=SLOW_MO_V)
    if os.path.isfile("state_zhihu.json"):
        with open("state_zhihu.json") as f:
            storage_state = json.loads(f.read())
        context = browser.new_context(viewport={
            'width': 1440,
            'height': 860
        },
                                      storage_state=storage_state)
        page = context.new_page()
        page.goto(url)
        logger.info("🐶免认证登录成功")
    else:
        logger.info("😞免认证登录失败，请打开切换开发环境(ENV=DEV)手动验证...")
        context = browser.new_context(viewport={'width': 1440, 'height': 860})
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
        page.locator('button:has-text("登录") >> nth=1').click()
        page.wait_for_timeout(10000)
        storage = context.storage_state()
        with open("state_zhihu.json", "w") as f:
            f.write(json.dumps(storage))
        page.goto(url)
        logger.info('登录成功！')
    return (browser, context, page)