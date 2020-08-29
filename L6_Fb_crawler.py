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
        
        for i in range(1, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(i)
            time.sleep(3)
                
        check = True
        test = 0
        while check:
            print(test)
            # 變成開啟留言 + 貼文內容
            show_more_comments = driver.find_elements_by_css_selector("span.j83agx80.fv0vnmcu.hpfvmrgz span.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.lrazzd5p.m9osqain")
            for show_more_comment in show_more_comments:
                if show_more_comment.text != '':
                    ActionChains(driver).move_to_element(show_more_comment).perform()
                    show_more_comment.click()

            show_more_contents = driver.find_elements_by_css_selector("div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.oo9gr5id.gpro0wi8.lrazzd5p")
            for show_more_content in show_more_contents:
                if show_more_comment.text != '':
                    ActionChains(driver).move_to_element(show_more_content).perform()
                    show_more_content.click()
                
            print('open reply')
            time.sleep(2)
            if(len(show_more_comments) == 0 and len(show_more_contents) == 0):
                check = False
            test = test + 1
        
        sourceCode = BeautifulSoup(driver.page_source)
        article_box = sourceCode.select('div.k4urcfbm.dp1hu0rb.d2edcug0.cbu4d94t.j83agx80.bp9cbjyn')[0]
        articles = article_box.select('div.du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0')
        for article in articles:
            
            date = content = promotion_date = ''
            attach = interactive = promotion_attach = promotion_interactive = replied_count = shared_count = good = 0
            
            # FB 2.0 更新 - 時間 + post id 取得，因為日期不再具有唯一性，只剩日期沒有時間，無法當做貼文的唯一值
            date_post_id_element = article.select('div.oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw')[0]
            post_path = date_post_id_element['href']
            start = post_path.find('posts/')
            end = post_path.find('?')
            post_id = post_path[start+6:end]
            article_date = date_post_id_element.text
            ## 2020年10月9日 => 2020-10-9
            article_date = article_date.replace('年', '-').replace('月', '-').replace('日','')
            ## 2020-10-9 => ['2020', '10', '9']
            article_date_list = article_date.split('-')
            ## ['2020', '10', '9'] => ['2020', '10', '09']
            if int(article_date_list[1]) < 10:
                article_date_list[1] = '0' + article_date_list[1]
            if int(article_date_list[2]) < 10:
                article_date_list[2] = '0' + article_date_list[2]
            ## ['2020', '10', '09'] => '2020-10-09'
            article_date = article_date_list.joins('-')
            print('date: ' + article_date)
            
            if( article_date > '2016-01-01' ):
            # FB 2.0 更新 - 時間取得 end
                content = ''
                # FB 2.0 更新 - 貼文內容取得更直觀
                show_contents = article.select('div.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.knj5qynh.oo9gr5id.hzawbc8m > div')
                for show_content in show_contents:
                    content = content + show_content.text + '。'

                content = content.replace("'", "\'").replace('"', '\"')
                print('content: ' + content)

                # FB 2.0 更新 - 貼文成效資料區塊更直覺
                # 由於 class 過長，所以會先用類似 attach_number 的形式，用 list 儲存兩個資料
                # 並在分別取出，設定在對應的變數中
                attach_number = article.select('span.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.lrazzd5p.oo9gr5id.hzawbc8m')
                attach = attach_number[0].text.replace(',', '')
                interactive = attach_number[1].text.replace(',', '')
                promotion_element = article.select('div.pybr56ya.scb9dxdr.dflh9lhu.f10w8fjw.cbu4d94t.a8c37x1j')
                if(len(promotion_element) > 0):
                    
                    promotion_string = promotion_element.select('div.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.a8c37x1j.muag1w35.dco85op0.e9vueds3.j5wam9gi.knj5qynh.oo9gr5id.hzawbc8m')[0].text
                    promotion_date = promotion_string.split('：')[1]
                    promotion_number = promotion_element.select('div.a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7.ltmttdrg.g0qnabr5.oi732d6d.ik7dh3pa.d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.muag1w35.enqfppq2.jq4qci2q.a3bd9o3v.lrazzd5p.oo9gr5id.hzawbc8m')
                    promotion_attach = promotion_number[0].text.replace(',', '')
                    promotion_interactive = promotion_number[1].text.replace(',', '')

                    print('promotion_date: ' + promotion_date)
                    print('promotion_attach: ' + promotion_attach)
                    print('promotion_interactive: ' + promotion_interactive)

                print('attach: ' + attach)
                print('interactive: ' + interactive)

                # FB 2.0 更新 - 互動資料區塊
                # 留言和分享併為同樣的 class，所以整合起來，用 for 迴圈過濾
                # 如果有抓到『留言』或『分享』，則判斷為留言或分享的資料文字
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
                # 本來拿日期為 key，改拿 post_id
                sql = '''SELECT * FROM `fb_social_data`.`posts` WHERE id = '{}'
                    '''.format(post_id)  
                cursor.execute(sql)
                posts = cursor.fetchall()

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
                              VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')'''.format(
                    post_id, date, content, attach, interactive, promotion_date, promotion_attach, promotion_interactive,
                    replied_count, shared_count, good)

                cursor.execute(sql)
                connection.commit()                

                sql = ''' SELECT * FROM fb_social_data.posts WHERE date = '{}'; '''.format(date)
                cursor.execute(sql)
                posts = cursor.fetchall()
                post_id = posts[0]['id']

                sql = ''' DELETE FROM fb_social_data.replies WHERE post_id = '{}'; '''.format(post_id)
                cursor.execute(sql)
                connection.commit() 

                replied_comments = article.select('span._3l3x')
                for replied_comment in replied_comments:
                    replied_text = replied_comment.text
                    replied_text = replied_text.replace("'", "\'").replace('"', '\"')
                    sql = ''' INSERT INTO fb_social_data.replies(comment, post_id) 
                              VALUES('{}', '{}')'''.format(replied_text, post_id)
                    cursor.execute(sql)
                    connection.commit() 
                    print('replied_text: '+ replied_text)
                
        
    connection.close()
#     driver.close()
except Exception :
    print(traceback.format_exc())
    connection.close()
    driver.close()
    