from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time 
import os
from datetime import datetime, date, timedelta
import pymysql.cursors
import traceback
from dotenv import load_dotenv
load_dotenv()
deadline = str(date.today() + timedelta(weeks= -26))
               
connection = pymysql.connect(host='localhost',
                             user='root', 
                             password='password', 
                             db='fb_social_data', 
                             cursorclass=pymysql.cursors.DictCursor)

options = Options()
options.add_argument("--disable-notifications")
# options.add_argument('--headless')
options.experimental_options["prefs"] = {'profile.default_content_settings' : {"images": 2}, 
                                        'profile.managed_default_content_settings' :  {"images": 2}}
driver = webdriver.Chrome(os.getcwd() + '/chromedriver', chrome_options=options)

def parse_date(text):
    if text.find('年') > 0:
        ## 2020年10月9日 => 2020-10-9
        article_date = text.replace('年', '-').replace('月', '-').replace('日','')
        ## 2020-10-9 => ['2020', '10', '9']
        article_date_list = article_date.split('-')

        ## ['2020', '10', '9'] => ['2020', '10', '09']
        if int(article_date_list[1]) < 10:
            article_date_list[1] = '0' + article_date_list[1]
        if int(article_date_list[2]) < 10:
            article_date_list[2] = '0' + article_date_list[2]
        ## ['2020', '10', '09'] => '2020-10-09'
        article_date = '-'.join(article_date_list)
        return article_date
    else:
        return False
try:
    with connection.cursor() as cursor:
        driver.get('https://www.facebook.com')
        driver.execute_script("document.getElementById('facebook').className = ''");
        username = driver.find_elements_by_css_selector("input[name=email]")[0]
        password = driver.find_elements_by_css_selector("input[name=pass]")[0]
        username.send_keys(os.getenv("EMAIL"))
        password.send_keys(os.getenv("PASSWORD"))
        login_button = driver.find_elements_by_css_selector("button[type=submit]")[0]
        # set size
        driver.set_window_size(1024, 768)
        login_button.click()
        time.sleep(2)
        driver.get('https://www.facebook.com/farmbridger/')

        for i in range(1, 2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        content_ids = []
        keep_craw = True
        while keep_craw:
            # 頁面程式碼初始化
            sourceCode = BeautifulSoup(driver.page_source)
            article_box = sourceCode.select('div.k4urcfbm.dp1hu0rb.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn')[0]
            articles = article_box.select('[class="lzcic4wl"][role="article"]')
            for article in articles:
                # 設定預設變數
                date = date_text = content = promotion_date = ''
                attach = interactive = promotion_attach = promotion_interactive = replied_count = shared_count = good = 0 

                # 設定與檢查內容 id，確認是否有爬過
                content_id = article.get('aria-describedby')
                article_id = article['aria-labelledby']
                if content_id != None:
                   content_id = content_id.split(' ')[1]

                if content_id in content_ids:
                    continue

                if content_id == None:
                    print(article)
                    driver.execute_script("window.scrollTo(0, window.pageYOffset + window.innerHeight);")
                    time.sleep(5)
                    break
                content_ids.append(content_id)

                # 檢查時間
                time_flag_contents = article.select('div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw')
                for time_flag_content in time_flag_contents:
                    date_text = time_flag_content.text
                    date = parse_date(date_text)
                    print(date)
                    if( date != False and date > deadline ):
                        pass
                    elif( date == False ):
                        pass
                    else:
                        keep_craw = False
                        break
                # 抓出 post, photo, video 的 id
                time_element = driver.find_element_by_xpath("//div[@aria-label='{}']".format(date_text))
                ActionChains(driver).move_to_element(time_element).perform()
                time_element = driver.find_element_by_xpath("//a[@aria-label='{}']".format(date_text))
                post_path = time_element.get_attribute('href')
                if post_path.find('/posts/') > 0:
                    start = post_path.find('/posts/') + 7
                    end = post_path.find('?')
                    post_id = post_path[start:end]
                elif post_path.find('/photos/') > 0:
                    start = post_path.find('a.') + 19
                    end = start + 16
                    post_id = post_path[start:end]
                elif post_path.find('/videos/') > 0:
                    start = post_path.find('/videos/') + 8
                    end = post_path.find('?') - 1
                    post_id = post_path[start:end]
                else:
                    post_id = 1
                print(post_id)

                # 點擊『更多』按鈕
                article_more_button = driver.find_elements_by_css_selector('div#{} div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.oo9gr5id.gpro0wi8.lrazzd5p'.format(content_id))[0]
                ActionChains(driver).move_to_element(article_more_button).perform()
                article_more_button.click()
                # 點擊後，重新讀取頁面 html 程式碼
                sourceCode = BeautifulSoup(driver.page_source)
                article_box = sourceCode.select('div.k4urcfbm.dp1hu0rb.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn')[0]
                article = article_box.select('[class="lzcic4wl"][role="article"][aria-labelledby="{}"]'.format(article_id))[0]
                # 獲得貼文資料
                show_contents = article.select('span.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.knj5qynh.oo9gr5id.hzawbc8m > div')
                for show_content in show_contents:
                    content = content + show_content.text + '。'
                content = content.replace("'", "\'").replace('"', '\"')
                print('content: ' + content)
                # 獲得廣告成效資料
                attach_number = article.select('span.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.lrazzd5p.oo9gr5id.hzawbc8m')
                attach = attach_number[0].text.replace(',', '')
                interactive = attach_number[1].text.replace(',', '')
                promotion_element = article.select('div.pybr56ya.scb9dxdr.dflh9lhu.f10w8fjw.cbu4d94t.a8c37x1j')
                if(len(promotion_element) > 0):
                    
                    promotion_string = promotion_element[0].select('span.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.dco85op0.e9vueds3.j5wam9gi.knj5qynh.oo9gr5id.hzawbc8m')[0].text
                    promotion_date = promotion_string.split('：')[1]
                    promotion_number = promotion_element[0].select('span.a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7.ltmttdrg.g0qnabr5.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.lrazzd5p.oo9gr5id.hzawbc8m')
                    promotion_attach = promotion_number[0].text.replace(',', '')
                    promotion_interactive = promotion_number[1].text.replace(',', '')

                    print('promotion_date: ' + promotion_date)
                    print('promotion_attach: ' + promotion_attach)
                    print('promotion_interactive: ' + promotion_interactive)

                print('attach: ' + attach)
                print('interactive: ' + interactive)
                # 獲得社群互動資料
                good = article.select('span.gpro0wi8.pcp91wgn')[0].text.replace(',', '')
                action_elements = article.select('div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.l9j0dhe7.abiwlrkh.gpro0wi8.dwo3fsh8.ow4ym5g4.auili1gw.du4w35lb.gmql0nx0')
                for action_element in action_elements:
                    if( action_element.text.find('留言') > 0 ):
                        replied_count = action_element.text.split('則')[0].replace(',', '')
                        print('replied_count: ' + replied_count)
                    if( action_element.text.find('分享') > 0):
                        shared_count = action_element.text.split('次')[0].replace(',', '')
                        print('share_count: ' + shared_count)
                    print('good: ' + good)
                sql = '''SELECT * FROM `fb_social_data`.`posts` WHERE id = '{}'
                    '''.format(post_id)  
                cursor.execute(sql)
                posts = cursor.fetchall()
                # 更新或刪除貼文
                if(len(posts) > 0):
                    sql = ''' UPDATE fb_social_data.posts SET date = '{}', 
                                content = '{}', 
                                attach = '{}', 
                                interactive = '{}', 
                                promotion_date = '{}', 
                                promotion_attach = '{}',
                                promotion_interactive = '{}', 
                                replied_count = '{}', 
                                shared_count = '{}', 
                                good = '{}' Where (id = '{}')'''.format(
                    date, content, attach, interactive, promotion_date, promotion_attach, promotion_interactive,
                    replied_count, shared_count, good, post_id)

                else:
                    sql = ''' INSERT INTO fb_social_data.posts(id, date, content, attach, interactive, promotion_date, promotion_attach,
                                        promotion_interactive, replied_count, shared_count, good) 
                            VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')'''.format(
                    post_id, date, content, attach, interactive, promotion_date, promotion_attach, 
                    promotion_interactive, replied_count, shared_count, good)

                cursor.execute(sql)
                connection.commit()

                sql = ''' DELETE FROM fb_social_data.replies WHERE post_id = '{}'; '''.format(post_id)
                cursor.execute(sql)
                connection.commit() 
                # 點擊回覆中的按鈕
                init_comment_button = driver.find_elements_by_css_selector("div[aria-labelledby='{}'] span.j83agx80.fv0vnmcu.hpfvmrgz".format(article_id))
                if len(init_comment_button) > 0:
                    ActionChains(driver).move_to_element(init_comment_button[0]).perform()
                    init_comment_button[0].click()
                    time.sleep(2)
                    check_more_comments = True
                    while check_more_comments:
                        comment_buttons = driver.find_elements_by_css_selector("div[aria-labelledby='{}'] span.j83agx80.fv0vnmcu.hpfvmrgz".format(article_id))
                        for comment_button in comment_buttons:
                            ActionChains(driver).move_to_element(comment_button).perform()
                            comment_button.click()
                            time.sleep(1)
                        if len(comment_buttons) == 0:
                            check_more_comments = False
                    # 重新讀取程式碼
                    sourceCode = BeautifulSoup(driver.page_source)
                    article_box = sourceCode.select('div.k4urcfbm.dp1hu0rb.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn')[0]
                    article = article_box.select('[class="lzcic4wl"][role="article"][aria-labelledby="{}"]'.format(article_id))[0]
                    # 抓取回覆資料
                    replied_comments = article.select('div.tw6a2znq.sj5x9vvc.d1544ag0.cxgpxx05')
                    for replied_comment in replied_comments:
                        replied_text = replied_comment.text
                        replied_text = replied_text.replace("'", "\'").replace('"', '\"')
                        sql = ''' INSERT INTO fb_social_data.replies(comment, post_id) 
                                VALUES('{}', '{}')'''.format(replied_text, post_id)
                        cursor.execute(sql)
                        connection.commit() 
                        print('replied_text: '+ replied_text)
        
    connection.close()
    driver.close()
except Exception :
    print(traceback.format_exc())
    connection.close()
    driver.close()
    