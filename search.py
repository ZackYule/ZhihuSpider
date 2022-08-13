from ast import keyword
from json.tool import main
import json
import os
from playwright.sync_api import sync_playwright
from loguru import logger
from settings import *
from utils import *
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)

def login(p,keyword):
    browser = p.webkit.launch(headless=HEAD_V, slow_mo = SLOW_MO_V)
    if os.path.isfile("state_zhihu.json"):
        with open("state_zhihu.json") as f:
            storage_state = json.loads(f.read())
        context = browser.new_context(viewport={ 'width': 1440, 'height': 860 },storage_state=storage_state)
        page = context.new_page()
        page.goto(f"https://www.zhihu.com/search?q={keyword}")
        logger.info("免认证登录成功")
    else:
        logger.info("免认证登录失败，请打开有头模式手动验证...自动验证太难了555...")
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
        logger.info('登录成功！')
    return (browser, context, page)

def search_by_keyword(keyword):
    with sync_playwright() as p:
        # 登录
        browser, context, page = login(p,keyword)
        page.locator("[aria-label=\"搜索\"]").click()
        
        content_divs = page.locator("//div[@data-za-detail-view-path-module='AnswerItem']//div[@itemprop='zhihu:question']")

        question_divs_count = refresh_times = 0
        while True:
            logger.info('浏览数据中...')
            page.wait_for_timeout(1000)
            page.mouse.wheel(0,2000)

            new_question_divs_count = content_divs.count()
            logger.debug(new_question_divs_count)
            if question_divs_count == new_question_divs_count:
                refresh_times += 1
            else:
                refresh_times = 0
            if refresh_times >= MAX_REFRESH_TIMES:
                logger.info('刷新页面结束')
                break
            question_divs_count = new_question_divs_count
        
        logger.debug(content_divs.all_inner_texts())
        content_elements = content_divs.element_handles()

        logger.debug(len(content_elements) == content_divs.count())

        logger.info('开始写入数据...')
        for content_element in content_elements:
            item = {
                'title':content_element.query_selector("//meta[@itemprop='name']").get_attribute("content"),
                'url':content_element.query_selector("//meta[@itemprop='url']").get_attribute("content")}
            logger.debug(item)
            csv_pipeline(item, KEYWORD, item.keys())
        logger.info('写入完毕...')
        
        # page.pause()
        context.close()
        browser.close()

if __name__ == "__main__":
    search_by_keyword(KEYWORD)
    