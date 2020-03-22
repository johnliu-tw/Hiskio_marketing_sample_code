# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import pymysql
from datetime import date, timedelta


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('token')
# Channel Secret
handler = WebhookHandler('secret')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    connection = pymysql.connect (host='localhost',
                                    user='user',
                                    password='password',
                                    db='new_media',
                                    cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        cursor = connection.cursor()
        event_text = event.message.text
        text = ""
        text_array = []
        if(event_text.find("article") != -1):
            query = event_text.split(' ')[0]
            brand = event_text.split(' ')[2]
            if( query == 'week' ):
                time = str(date.today() - timedelta(weeks = 1))
                sql = ''' SELECT * FROM new_media.articles where date >= "{}" and brand = "{}" '''.format(time, brand)
                cursor.execute(sql)
                articles = cursor.fetchall()
                for article in articles:
                    text = text + '''{}, 相關tag: {}, 分享數: {}, 來源: {} \n\n'''.format(
                        article['title'].strip(), 
                        article['tags'], 
                        article['share'], 
                        article['brand'])
                    if(len(text) > 1000):
                        text_array.append(TextSendMessage(text=text))
                        text = ""
                    elif ( article == articles[-1]):
                        text_array.append(TextSendMessage(text=text))
                        text = ""
                    
            else:
                sql = ''' SELECT * FROM new_media.articles where date = "{}" and brand = "{}"'''.format(query, brand)
                cursor.execute(sql)
                articles = cursor.fetchall()
                for article in articles:
                    text = text + '''{}, 相關tag: {}, 分享數: {}, 來源: {} \n\n'''.format(
                        article['title'].strip(), 
                        article['tags'], 
                        article['share'], 
                        article['brand'])
                    if(len(text) > 1000):
                        text_array.append(TextSendMessage(text=text))
                        text = ""
                    elif ( article == articles[-1]):
                        text_array.append(TextSendMessage(text=text))
                        text = ""
        elif(event_text.find("facebook") != -1):
            query = event_text.split(' ')[0]
            promotion_attach = promotion_interactive = good = replied_count = 0 
            if( query == 'week' ):
                time = str(date.today() - timedelta(weeks = 1))
                sql = ''' SELECT * FROM fb_social_data.posts where date >= "{}" '''.format(time)
                cursor.execute(sql)
                posts = cursor.fetchall()
                for post in posts:
                    promotion_attach += post['promotion_attach']
                    promotion_interactive += post['promotion_interactive']
                    good += post['good']
                    replied_count += post['replied_count']
                    
                    
                text = '''本週貼文總觸及人數 {}, 互動人數: {}, 共 {} 讚, {} 個留言 \n\n'''.format(
                        promotion_attach,
                        promotion_interactive,
                        good,
                        replied_count)
                    
            else:
                sql = ''' SELECT * FROM fb_social_data.posts where date like "%{}%"'''.format(query)
                cursor.execute(sql)
                posts = cursor.fetchall()
                for post in posts:
                    promotion_attach += post['promotion_attach']
                    promotion_interactive += post['promotion_interactive']
                    good += post['good']
                    replied_count += post['replied_count']
                    
                    
                text = '''本週貼文總觸及人數 {}, 互動人數: {}, 共 {} 讚, {} 個留言 \n\n'''.format(
                        promotion_attach,
                        promotion_interactive,
                        good,
                        replied_count)      
            text_array.append(TextSendMessage(text=text))
        else:
            text_array.append(TextSendMessage(text='看謀啦～'))
    line_bot_api.reply_message(event.reply_token,text_array)
    connection.close()

import os
if __name__ == "__main__":
    app.run()
