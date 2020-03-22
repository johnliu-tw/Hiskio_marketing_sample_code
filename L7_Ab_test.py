import pandas as pd
import bokeh
import pymysql
import math
from scipy import stats
from bokeh.plotting import figure
from bokeh.io import show, output_notebook

connection = pymysql.connect (host='localhost',
                              user='root',
                              password='password',
                              db='fb_social_data',
                              cursorclass=pymysql.cursors.DictCursor)

sql = ''' SELECT * FROM fb_social_data.posts where promotion_attach > 0 '''
data = pd.read_sql(sql, con=connection)

control_date=[]
control_attach=[]
control_interactive=[]
control_rate=[]

test_attach=[]
test_interactive=[]
test_rate=[]

control_n=0
test_n=0

for index, row in data.iterrows():
    if row['group'] == 'control':
        control_attach.append(row['promotion_attach'])
        control_interactive.append(row['promotion_interactive'])
        control_rate.append(row['promotion_interactive']/row['promotion_attach'])  
        control_date.append(row['date'][0:10])
        control_n += 1
    else:
        test_attach.append(row['promotion_attach'])
        test_interactive.append(row['promotion_interactive'])
        test_rate.append(row['promotion_interactive']/row['promotion_attach'])  
        test_n += 1
        

avg_control_rate = sum(control_rate)/control_n
avg_test_rate = sum(test_rate)/test_n

print(test_rate)
print(avg_test_rate)

lift=-abs(avg_control_rate - avg_test_rate)
scale_one = avg_control_rate * (1-avg_control_rate) * (1/control_n)
scale_two = avg_test_rate * (1-avg_test_rate) * (1/test_n)
scale_val = math.sqrt(scale_one + scale_two)
p_value = 2 * stats.norm.cdf(lift, loc=0, scale=scale_val)

print(p_value)

p = figure(plot_width=400, plot_height=400, title='控制組貼文觸及次數成效')
p.multi_line([[ i for i in range(1, control_n+1)], [ i for i in range(1, control_n+1)]],
             [control_attach, control_interactive], color=['firebrick', 'Moccasin'])
p2 = figure(x_range=control_date, plot_width=400, plot_height=400, title='控制組貼文互動次數成效')
p2.vbar(x=control_date, top=control_interactive, width=0.5)

output_notebook()
show(p)
show(p2)

