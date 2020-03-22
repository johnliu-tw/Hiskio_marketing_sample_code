from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from bs4 import BeautifulSoup
import time 
import os
import csv
import pymysql.cursors

connection = pymysql.connect(host='localhost', 
                             user='root', 
                             password='password', 
                             db='new_media', 
                             cursorclass=pymysql.cursors.DictCursor)

from datetime import date
today = date.today()
search_date = today.strftime('%-m/%d')
file_date = today.strftime('%-m-%d')

options = Options()

driver = webdriver.Chrome(os.getcwd() + '/chromedriver', chrome_options=options)

try:
    with connection.cursor() as cursor:
        with open(file_date+'data.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
            driver.get('https://www.ptt.cc/bbs/NBA/index.html')
            sourceCode = BeautifulSoup(driver.page_source)
            button = sourceCode.select('a.btn.wide')[1]
            x = button['href'].find('x')
            dot = button['href'].find('.')
            index = button['href'][x+1:dot]

            for i in range(int(index)+1, 6495, -1):
                print(i)
                driver.get('https://www.ptt.cc/bbs/NBA/index'+str(i)+'.html')
                sourceCode = BeautifulSoup(driver.page_source)
                metaSection = sourceCode.select('div.r-list-container')[0]
                sections = metaSection.select('div.r-ent')
                for section in sections:
                    title = section.select('div.title')[0].text
                    num = section.select('div.nrec')[0].text
                    author = section.select('div.author')[0].text
                    date = section.select('div.date')[0].text

                    title = title.strip()
                    if(title.startswith('[公告]')):
                        continue

                    if(num.find('爆') != -1):
                        num = '100'
                    if(num.find('X') != -1  or num == ''):
                        num = '0'

                    if(date.strip() == search_date):              
                        print(title)
                        print(num)
                        print(author)
                        print(date)

                        writer = csv.writer(csvfile)
                        writer.writerow([num, title, author, date])
                        sql = '''
                        INSERT INTO `new_media`.`ptt` (`title`, `num`, `author`, `date`)
                        VALUES('{}', '{}', '{}', '{}')
                        '''.format(title, num, author, date)  
                        print(sql)
                        cursor.execute(sql)
                        connection.commit()
                        
    connection.close()
    driver.close()
except Exception as e:
    print(e)
    connection.close()
    driver.close()