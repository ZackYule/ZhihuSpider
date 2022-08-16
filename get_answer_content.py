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
    logger.info(f'开始爬取问题：{title}')
    logger.debug(f'问题网址：{url}')

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
        
        answer_divs_count = invalid_refresh_times = 0
        while answer_divs.count() <= max_num_of_answers:
            logger.info(f'浏览数据中... 已经浏览了{answer_divs_count}条回答')
            page.wait_for_timeout(1000)
            safe_drag_list(answer_divs, page)
     
            new_answer_divs_count = answer_divs.count()
            logger.debug(new_answer_divs_count)
            if answer_divs_count >= new_answer_divs_count:
                invalid_refresh_times += 1
            else:
                invalid_refresh_times = 0
            if invalid_refresh_times >= MAX_INVALID_REFRESH_TIMES:
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
    content_list = get_content_info_from_csv(KEYWORD, '问题链接')
    for content_item in content_list:
        get_QA_info_from_url(content_item, MAX_NUM_OF_ANSWERS)