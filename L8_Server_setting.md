## Server 初始設定
1. sudo apt-get update
2. sudo apt-get install apache2 libapache2-mod-wsgi-py3 python-virtualenv python3-pip -y
3. sudo apt-get update
4. sudo apt-get install apache2 libapache2-mod-wsgi-py3 python-virtualenv python3-pip -y
5. mkdir flaskapp
6. sudo ln -sT ~/flaskapp /var/www/html/flaskapp
7. touch flaskapp/index.html 
8. echo "Hello World" > flaskapp/index.html
9. sudo apachectl restart
10. http://35.221.146.213/flaskapp/index.html

## Python 設定
1. pip3 install virtualenv
2. git pull 
3. cd flaskapp
4. virtualenv -p python3 env
5. source env/bin/activate  
6. pip3 install flask
7. touch flaskapp.wsgi
```python
import sys
sys.path.insert(0, '/var/www/html/flaskapp')
sys.path.insert(1, '/home/service/flaskapp/new_env/lib/python3.6/site-packages')
from main import app as application
```

8. Set apache config
/etc/apache2/sites-enabled/000-default.conf

```apacheconf
        WSGIDaemonProcess flaskapp python-path=/var/www/html/flaskapp:/var/www/html/flaskapp/env/lib/python3.6/site-packages
        WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi

        DocumentRoot /var/www/html

        <Directory flashapp>
                WSGIProcessGroup flaskapp
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
        </Directory>
```

9. sudo apachectl restart
http://35.221.146.213/


## 安裝 Line Developer
1. source env/bin/activate
2. Pip3 install line-bot-sdk
3. sudo apt-get update
4. sudo apt-get install software-properties-common -y
5. sudo add-apt-repository ppa:certbot/certbot
6. sudo apt-get update
7. sudo apt-get install python-certbot-apache -y
8. sudo vim /etc/apache2/sites-enabled/000-default.conf
9. Comment WSGIDaemonProcess
10. sudo certbot --apache
11. Uncomment WSGIDaemonProcess
12. sudo apachectl restart

## 安裝資料庫
1. sudo apt-get install mysql-server mysql-client libmysqlclient-dev -y
2. sudo netstat -tap | grep mysql
3. sudo vim /etc/mysql/debian.cnf
4. mysql -u debian-sys-maint -p

### Create User
```sql
CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'user'@'%' IDENTIFIED BY 'password';
GRANT ALL ON *.* TO 'user'@'localhost' IDENTIFIED BY 'password' WITH GRANT OPTION;
GRANT ALL ON *.* TO 'user'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION;
FLUSH PRIVILEGES; 
EXIT;
```

### Create Schema
```sql
CREATE DATABASE `new_media` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
CREATE TABLE `new_media`.`articles ` (   `id` int(11) NOT NULL AUTO_INCREMENT,   `title` TEXT DEFAULT NULL,   `date` varchar(45) DEFAULT NULL,   `tags` TEXT DEFAULT NULL,   `share` varchar(45) DEFAULT NULL,   `brand` varchar(45) DEFAULT NULL,    PRIMARY KEY (`id`) ) ENGINE=InnoDB AUTO_INCREMENT=397 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE DATABASE `fb_social_data` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
CREATE TABLE `fb_social_data`.`posts` ( `id` int(11) NOT NULL AUTO_INCREMENT, `date` varchar(45) DEFAULT NULL, `content` text, `attach` int(11) DEFAULT NULL, `interactive` int(11) DEFAULT NULL, `promotion_date` varchar(45) DEFAULT NULL, `promotion_attach` int(11) DEFAULT NULL, `promotion_interactive` int(11) DEFAULT NULL, `replied_count` int(11) DEFAULT NULL, `shared_count` int(11) DEFAULT NULL, `good` int(11) DEFAULT NULL, `group` varchar(45) DEFAULT NULL, PRIMARY KEY (`id`) ) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
CREATE TABLE `fb_social_data`.`replies` ( `id` int(11) NOT NULL AUTO_INCREMENT, `comment` text, `post_id` int(11) DEFAULT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=854 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```

## 安裝 chrome 
1. sudo apt-get install libxss1 libappindicator1 libindicator7 xvfb unzip -y
2. wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
3. sudo apt-get install -f -y( run when install error )
4. sudo dpkg -i google-chrome-stable_current_amd64.deb
google-chrome --version
https://chromedriver.storage.googleapis.com/index.html
5. wget -N https://chromedriver.storage.googleapis.com/{version}/chromedriver_linux64.zip
6. unzip chromedriver_linux64.zip
7. chmod +x chromedriver


## FB資料庫更新

1. 設定 port 號開啟
2. 連進 /etc/mysql/mysql.conf.d/mysqld.cnf 更改 bind-address 成 0.0.0.0
3. /usr/local/mysql/bin/mysqldump -u root --password="password" -e "fb_social_data" > db.sql

       Windows
       路徑: C:\Program Files\MySQL\MySQL Server 8.0\bin
       輸出的位置: C:\Users\user\Desktop\db.sql

5. /usr/local/mysql/bin/mysql -h 35.201.183.55 -u user --password="password" --execute="DROP DATABASE fb_social_data;"
6. /usr/local/mysql/bin/mysql -h 35.201.183.55 -u user --password="password" --execute="CREATE SCHEMA fb_social_data DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
7. /usr/local/mysql/bin/mysql -h 35.201.183.55 -u user --password="password" --database="fb_social_data"  < "/Users/johnliu/db.sql"
8. 建立 bash script 檔案 
#!/bin/bash
