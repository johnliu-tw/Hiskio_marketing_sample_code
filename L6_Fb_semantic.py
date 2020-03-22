import pymysql.cursors
import jieba
from snownlp import SnowNLP
import pprint
pp = pprint.PrettyPrinter(indent=4)

connection = pymysql.connect(host='localhost', 
                             user='root', 
                             password='password', 
                             db='fb_social_data', 
                             cursorclass=pymysql.cursors.DictCursor)
with connection.cursor() as cursor:
    sql = ''' SELECT * FROM fb_social_data.replies where post_id = '{}' '''.format(15)
    cursor.execute(sql)
    replies = cursor.fetchall()
    text_dict = {}
    for replie in replies:
        seg_list = jieba.cut(replie['comment']) 
        for seg in seg_list:
            if seg in text_dict:
                text_dict[seg] += 1
            else: 
                text_dict[seg] = 1
                
    sentiments_dict = {}
    for replie in replies:
        s = SnowNLP(replie['comment'])
        sentiments_dict[replie['comment']] = s.sentiments
    
    seg_data = sorted(text_dict.items(), key=lambda d:d[1], reverse=True)
    pp.pprint(seg_data)
    sentiments_data = sorted(sentiments_dict.items(), key=lambda d:d[1], reverse=True)
    pp.pprint(sentiments_data)
connection.close()