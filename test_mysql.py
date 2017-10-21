#!/usr/bin/python3
import pymysql
conn = pymysql.connect(host='192.168.123.124', port=3308, user='inven', passwd='eric20000', db='coolroid')
# conn = pymysql.connect(host='127.0.0.1', port=3306, user='inven', passwd='eric20', db='mysql')
cursor = conn.cursor()

date1 = input('Input you date1: ')
date2 = input('Input you date2: ')
cursor.execute("select count(menu_item_id), menu_item_id, menu_item_name, unit from history_order_detail where order_time "
               "between %s and %s and menu_item_id > 0 "
               "group by menu_item_id order by menu_item_name;", (date1, date2))
row = cursor.fetchall()
for a,b,c,d in row:
    print(c, 'total', a)

conn.commit()
cursor.close()
conn.close()