from playwright.sync_api import sync_playwright
from settings import *
from utils import *
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)


def search_by_keyword(keyword, max_num_of_questions = 100000):
    with sync_playwright() as playwright:
        # 登录
        base_url = f"https://www.zhihu.com/search?q={keyword}"
        browser, context, page = login(playwright, base_url)
        page.locator("[aria-label=\"搜索\"]").click()
        
        content_divs = page.locator("//div[@data-za-detail-view-path-module='AnswerItem']//div[@itemprop='zhihu:question']")

        question_divs_count = refresh_times = 0
        while content_divs.count() <= max_num_of_questions:
            logger.info('浏览数据中...')
            page.wait_for_timeout(1000)
            # page.mouse.wheel(0,2000)
            content_divs.last.scroll_into_view_if_needed()
            answer_div_height = content_divs.last.bounding_box()['height']
            page.mouse.wheel(0,answer_div_height/2)

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
            csv_pipeline(item, KEYWORD, '问题链接', item.keys())
        logger.info('写入完毕...')
        
        # page.pause()
        context.close()
        browser.close()

if __name__ == "__main__":
    search_by_keyword(KEYWORD, MAX_NUM_OF_QUESTIONS)
    