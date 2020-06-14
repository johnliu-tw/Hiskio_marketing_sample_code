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
        login_button = driver.find_elements_by_css_selector("input[type=submit]")[0]
        # set size
        driver.set_window_size(1024, 768)
        login_button.click()
        time.sleep(2)
        driver.get('https://www.facebook.com/farmbridger/')
        
        for i in range(1, 50):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(i)
            time.sleep(2)
                
        check = True
        while check:
            show_more_comments = driver.find_elements_by_css_selector("a._4sxc._42ft")
            for show_more_comment in show_more_comments:
                ActionChains(driver).move_to_element(show_more_comment).perform()
                show_more_comment.click()

            show_more_contents = driver.find_elements_by_css_selector("a._5v47.fss")
            for show_more_content in show_more_contents:
                ActionChains(driver).move_to_element(show_more_content).perform()
                show_more_content.click()
                
            print('open reply')
            time.sleep(2)
            if(len(show_more_comments) == 0 and len(show_more_contents) == 0):
                check = False
        
        sourceCode = BeautifulSoup(driver.page_source)
        article_box = sourceCode.select('div._1xnd')[1]
        articles = article_box.select('div._5pcr.userContentWrapper')
        for article in articles:
            
            date = content = promotion_date = ''
            attach = interactive = promotion_attach = promotion_interactive = replied_count = shared_count = good = 0
            
            utime = article.select('abbr._5ptz')[0]['data-utime']
            date = datetime.fromtimestamp(int(utime))
            checkdate = date.strftime('%Y-%m-%d')
            print('date: ' + str(date))
            
            if( checkdate > '2016-01-01' ):
                content = ''
                if(len(article.select('div.text_exposed_root')) == 0):
                    show_contents = article.select('div.userContent > p')
                    for show_content in show_contents:
                        content = content + show_content.text + '。'
                else:
                    show_contents = article.select('div.text_exposed_root > p')
                    hide_contents = article.select('div.text_exposed_show > p')
                    for show_content in show_contents:
                        content = content + show_content.text + '。'
                    for hide_content in hide_contents:
                        content = content + hide_content.text + '。'
                content = content.replace("'", "\'").replace('"', '\"')
                print('content: ' + content)
                if(len(article.select('tr._51mx')) > 0):
                    attach = article.select('td._51m-.vMid.hLeft span')[0].text.replace(',', '')
                    interactive = article.select('td._51mw._51m-.vMid.hLeft span')[0].text.replace(',', '')
                    if(len(article.select('div._6r-l div._ohe.lfloat div')) > 0):
                        promotion_string = article.select('div._6r-l div._ohe.lfloat div')[0].text
                        promotion_date = promotion_string.split('：')[1]
                        promotion_attach = article.select('div._6r-n')[0].text.replace(',', '')
                        promotion_interactive = article.select('div._6r-n')[1].text.replace(',', '')

                        print('promotion_date: ' + promotion_date)
                        print('promotion_attach: ' + promotion_attach)
                        print('promotion_interactive: ' + promotion_interactive)

                    print('attach: ' + attach)
                    print('interactive: ' + interactive)

                good = article.select('span._81hb')[0].text.replace(',', '')
                replied_elements = article.select('span._1whp._4vn2')
                shared_elements = article.select('span._355t._4vn2')
                if(len(replied_elements) > 0):
                    replied_count = replied_elements[0].text.split('則')[0].replace(',', '')
                    print('replied_count: ' + replied_count)
                if(len(shared_elements) > 0):
                    shared_count = shared_elements[0].text.split('次')[0].replace(',', '')
                    print('share_count: ' + shared_count)
                print('good: ' + good)

                sql = '''SELECT * FROM `fb_social_data`.`posts` WHERE date = '{}'
                    '''.format(date)  
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
                                  good = '{}' Where (date = '{}')'''.format(
                    date, content, attach, interactive, promotion_date, promotion_attach, promotion_interactive,
                    replied_count, shared_count, good, date)

                else:
                    sql = ''' INSERT INTO fb_social_data.posts(date, content, attach, interactive, promotion_date, promotion_attach,
                                         promotion_interactive, replied_count, shared_count, good) 
                              VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')'''.format(
                    date, content, attach, interactive, promotion_date, promotion_attach, promotion_interactive,
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
    