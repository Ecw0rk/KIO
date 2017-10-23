#!/usr/bin/python3
import pymysql
import datetime
import requests
import json

tokenUrl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
sendMsg = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="

# Wechat send message.
def get_token():
    values = {'corpid': 'ww1b4984f713aa92ed', 'corpsecret': 'Z4CyZ6_xyXitoEjgGWR_l1SFaME4J7B7D-p3ovo-VbU'}
    req = requests.post(tokenUrl, params=values)
    data = json.loads(req.text)
    return data["access_token"]

def send_msg(msg):
    # input msg need to change str()
    url = sendMsg + get_token()
    # 填写接收人@all发给所有人，如果你只想发给组内账号为zhangsan的人，这里就填写zhangsan，如果是zhangsan和lisi,那么就写 zhangsan|lisi
    values = """{"touser" : "ChenJiaYu|LaoPanNiang", 
      "msgtype":"text",
      "agentid":"1000002",
      "text":{
        "content": "%s"30
      },
      "safe":"0"
      }""" % msg
    requests.post(url, values)

def getItem():
    # 这个模块为了提取menu下的item
    conn = pymysql.connect(host='localhost',
                                 user='admin',
                                 password='eric20000',
                                 db='inventory')
    try:
        with conn.cursor() as cursor:
            sql = "select mid, menu_item_name, unit, in_id, show_remain, in_count from menu"
            # sql = "select menu_item_name, unit, inventory, mid from menu join inventory on menu.in_id = inventory.in_id"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except ConnectionError:
        print("Error to connect databases")
    finally:
        conn.close()

def searchInventory(in_id):
    # 这个模块输入in_id获取inventory
    conn = pymysql.connect(host='localhost',
                                 user='admin',
                                 password='eric20000',
                                 db='inventory')
    try:
        with conn.cursor() as cursor:
            sql = "select inventory, item from inventory where in_id = %s"
            cursor.execute(sql, (in_id))
            result = cursor.fetchall()
            return result
    except ConnectionError:
        print("Error to connect databases")
    finally:
        conn.close()

def countItems(menu_item_name, unit):
    # 这个模块为了统计item这一周的使用情况
    day2 = datetime.datetime.now().strftime('%Y-%m-%d')     # today
    day1 = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')     # One weeks ago
    conn = pymysql.connect(host='192.168.123.124',
                                 port=3308,
                                 user='inven',
                                 password='eric20000',
                                 db='coolroid')
    if unit != None:    # compare if unit equal None
        try:
            with conn.cursor() as cursor:
                # sql = "select count(*), menu_item_name, unit from history_order_detail where menu_item_name = %s and unit = %s" \
                #       "and order_time between %s and %s"
                sql = "select count(*) from history_order_detail where menu_item_name = %s and unit = %s and order_time between %s and %s"
                cursor.execute(sql, (menu_item_name, unit, day1, day2))
                result = cursor.fetchall()
                return result
        except ConnectionError:
            print("Error to connect databases")
        finally:
            conn.close()
    else:
        try:
            with conn.cursor() as cursor:
                # sql = "select count(*), menu_item_name, unit from history_order_detail where menu_item_name = %s" \
                #       "and order_time between %s and %s"
                sql = "select count(*) from history_order_detail where menu_item_name = %s" \
                      "and order_time between %s and %s"
                cursor.execute(sql, (menu_item_name, day1, day2))
                result = cursor.fetchall()
                return result
        except ConnectionError:
            print("Error to connect databases")
        finally:
            conn.close()

def cal():
    msg = []
    conn = pymysql.connect(host='localhost',
                                 user='admin',
                                 password='eric20000',
                                 db='inventory')
    items = getItem()
    for mid, menu_item_name, unit, in_id, show_remain, in_count in items:
        # inventory = searchInventory(in_id)[0][0]
        for inventory, item in searchInventory(in_id):
            weeksold = countItems(menu_item_name, unit)[0][0]
            inventory = inventory - weeksold * in_count
            if show_remain == 1:    # show_remain等于0只显示卖出数量,等于1显示卖出数量和库存数量,等于2什么都不显示,等于3只显示库存名称和数量
                if weeksold != 0:
                    if unit == None:
                        msg.append('%s sold %d remain: %d' % (menu_item_name, weeksold, inventory))
                    else:
                        msg.append('%s %s sold %d remain: %d' % ( menu_item_name, unit, weeksold, inventory))
                else:
                    if unit == None:
                        msg.append('%s sold %d remain: %d' % ( menu_item_name, weeksold, inventory))
                    else:
                        msg.append('%s %s sold %d remain: %d' % (menu_item_name, unit, weeksold, inventory))
            elif show_remain == 0:
                if weeksold != 0:
                    if unit == None:
                        msg.append('%s sold %d' % (menu_item_name, weeksold))
                    else:
                        msg.append('%s %s sold %d' % (menu_item_name, unit, weeksold))
                else:
                    if unit == None:
                        msg.append('%s sold %d' % (menu_item_name, weeksold))
                    else:
                        msg.append('%s %s sold %d' % (menu_item_name, unit, weeksold))
            elif show_remain == 3:
                msg.append('%s remain: %d' % (item, inventory))
            with conn.cursor() as cursor:
                sql = "update inventory join menu on inventory.in_id = menu.in_id set inventory=%s where menu.mid = %s"
                cursor.execute(sql, (inventory, mid))
                conn.commit()
    conn.close()
    message = '\n\n'.join(msg)
    return message

def main():
    # cal()
    message = cal()
    print(message)
    send_msg(message)
if __name__ == "__main__":
    main()
