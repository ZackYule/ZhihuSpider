from playwright.sync_api import sync_playwright
from settings import *
from utils import *
from loguru import logger
import sys

logger.remove()
handler_id = logger.add(sys.stderr, level=LOGGER_LEVEL)
logger.add('record.log', level='INFO', format='{time:DD-MMM-YYYY HH:mm:ss}|'
                  '{level:<8} '
                  '{message}')


def get_user_info_from_url(author_url):
    url = author_url
    logger.debug(f'作者网址：{url}')

    with sync_playwright() as playwright:
        # 记录信息
        info_item = {}
        info_item['主页'] = author_url
        # 登录
        browser, context, page = login(playwright, url)

        # 性别
        gender_male = page.locator("//*[local-name()='svg' and @class='Zi Zi--Male']")
        if gender_male.count() > 0:
            info_item['性别'] = '男'
        gender_male = page.locator("//*[local-name()='svg' and @class='Zi Zi--Female']")
        if gender_male.count() > 0:
            info_item['性别'] = '女'

        # page.pause()
        # 显示详细信息
        page.locator("//button[@class='Button ProfileHeader-expandButton Button--plain']").click()

        # id
        id_contents = page.locator("//h1[@class='ProfileHeader-title']//span").all_inner_texts()
        logger.debug(id_contents)
        info_item['昵称'] = id_contents[0].strip()
        info_item['签名'] = id_contents[1].strip()


        # ip地址
        info_item['ip属地'] = page.locator("//div[@class='UserCover-ipInfo']").inner_text().replace('IP 属地', '').strip()

        # 点赞板
        profile_div_list = page.locator("//div[@class='Profile-main']//div[@class='Card']/div[2]/div")

        for i in range(profile_div_list.count()):
            info_content = ' '.join(profile_div_list.nth(i).locator("xpath=./*[2]").all_inner_texts())
            info_item[info_content[0:2]] = info_content[2:].strip()
        
        # 粉丝板
        number_board = page.locator("//div[@class='NumberBoard FollowshipCard-counts NumberBoard--divider']")
        person_concerned_content = ' '.join(number_board.locator("xpath=./a[1]").all_inner_texts())
        followers_content = ' '.join(number_board.locator("xpath=./a[2]").all_inner_texts())
        info_item[person_concerned_content[0:3]] = person_concerned_content[3:].strip()
        info_item[followers_content[0:3]] = followers_content[3:].strip()

        detail_items = page.locator("//div[@class='ProfileHeader-detailItem']")
        logger.debug(detail_items)
        for i in range(detail_items.count()):
            title = detail_items.nth(i).locator("xpath=./span").inner_text()
            content = detail_items.nth(i).locator("xpath=./div").inner_text()
            info_item[title.strip()] = content.strip()

        logger.debug(info_item)

        # page.pause()
        context.close()
        browser.close()

        return info_item
    
def item_record(info_item:dict):
    logger.info('🌈开始写入数据...')

    target_info = USER_INFO_TITLE

    item = get_target_item(info_item, target_info)
    logger.debug(item)
    csv_pipeline(item, KEYWORD, '用户信息', item.keys())
    logger.info('🎉写入完毕!')

if __name__ == "__main__":
    author_url_list = get_column_info_info_from_csv(KEYWORD, '回答详情', 9)
    total_num = len(author_url_list)
    count = 0

    author_url_already_get = get_column_info_info_from_csv(KEYWORD, '用户信息', 15)

    for author_url in author_url_list:
        count += 1
        logger.info(f'🚀正在爬第{count}个用户，已完成{round(count/total_num*100, 2)}%的进度，网址是：{author_url}')

        if author_url not in author_url_already_get and author_url.split('/')[-1]:
            try:
                info_item = get_user_info_from_url(author_url)
                item_record(info_item)
            except Exception as e:
                logger.error(e)
                info_item = {'状态': '异常', '主页': author_url}
                item_record(info_item)


        # if count > 10:
        #     break