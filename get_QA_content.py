from playwright.sync_api import sync_playwright
from settings import *
from utils import *
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)


def get_QA_info_from_url(content_item, max_num_of_answers = 100000):
    url = content_item['url']
    title = content_item['title']

    with sync_playwright() as playwright:
        # 登录
        browser, context, page = login(playwright, url)

        # todo:这里要取一下问题的内容，下拉按钮要很久才能取到是为什么？

        # Click text=显示全部 ​
        # page.pause()
        # page.locator("text=显示全部​ ​").click()
        # page.locator(".QuestionHeader-tags")
        # question_content = page.locator("//div[@class='QuestionRichText QuestionRichText--expandable']']​").all_inner_texts()
        # logger.debug(question_content)

        answer_divs = page.locator("//div[@role='list']/div[@tabindex]")
        
        answer_divs_count = refresh_times = 0
        while answer_divs.count() <= max_num_of_answers:
            logger.info('浏览数据中...')
            page.wait_for_timeout(1000)
            answer_divs.last.scroll_into_view_if_needed()
            answer_div_height = answer_divs.last.bounding_box()['height']
            page.mouse.wheel(0,answer_div_height/2)
            # if answer_div_height > 860:
            #     logger.debug('太大放不下了...')    
            new_answer_divs_count = answer_divs.count()
            logger.debug(new_answer_divs_count)
            if answer_divs_count == new_answer_divs_count:
                refresh_times += 1
            else:
                refresh_times = 0
            if refresh_times >= MAX_REFRESH_TIMES:
                logger.info('刷新页面结束')
                break
            answer_divs_count = new_answer_divs_count

        answer_elements = answer_divs.element_handles()

        logger.info('开始写入数据...')
        for answer_element in answer_elements:
            item = {
                'title': title,
                'question_url': url,
                'answer_content': safe_get_field_from_element(answer_element, "//div[@class='RichContent-inner']"),
                'answer_url': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-time']/a","href"),
                'edit_time': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-time']/a"),
                'publish_time': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-time']/a/span","data-tooltip"),
                'voters_num': safe_get_field_from_element(answer_element, "//button[@aria-live and @aria-label]"), 
                'comments_num': safe_get_field_from_element(answer_element, "//button[@class='Button ContentItem-action Button--plain Button--withIcon Button--withLabel']"),
                'author_name': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-meta']/div[@itemprop='author']//meta[@itemprop='name']","content"),
                'author_url': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-meta']/div[@itemprop='author']//meta[@itemprop='url']","content"),
                'author_followerCount': safe_get_field_from_element(answer_element, "//div[@class='ContentItem-meta']/div[@itemprop='author']//meta[@itemprop='zhihu:followerCount']","content"),
                }
            logger.debug(item)
            csv_pipeline(item, KEYWORD, '回答详情', item.keys())
        logger.info('写入完毕...')

        # page.pause()
        context.close()
        browser.close()
    


if __name__ == "__main__":
    content_list = get_content_info_from_csv(KEYWORD)
    for content_item in content_list:
        get_QA_info_from_url(content_item, MAX_NUM_OF_ANSWERS)