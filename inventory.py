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
    # 填写接收人可以使用,分隔
    values = """{"touser" : "ChenJiaYu",
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
            sql = "select mid, menu_item_name, unit, in_id from menu"
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
            sql = "select inventory from inventory where in_id = %s"
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
    number = 0
    for mid, menu_item_name, unit, in_id in items:
        number += 1
        inventory = searchInventory(in_id)[0][0]
        weeksold = countItems(menu_item_name, unit)[0][0]
        inventory = inventory - weeksold
        if weeksold != 0:
            if unit == None:
                msg.append('%d %s sold %d remain %d' % (number, menu_item_name, weeksold, inventory))
            else:
                msg.append('%d %s %s sold %d remain %d' % (number, menu_item_name, unit, weeksold, inventory))
        else:
            if unit == None:
                msg.append('%d %s sold %d remain %d' % (number, menu_item_name, weeksold, inventory))
            else:
                msg.append('%d %s %s sold %d remain %d' % (number, menu_item_name, unit, weeksold, inventory))
        with conn.cursor() as cursor:
            sql = "update inventory join menu on inventory.in_id = menu.in_id set inventory=%s where menu.mid = %s"
            cursor.execute(sql, (inventory, mid))
            conn.commit()
    message = '\n'.join(msg)
    return message
    conn.close()


# def text():
#     msg = []
#     msg.append('%s to %s' % ((datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d')))
#     items = getItem()
#     for menu_item_name, unit in items:
#         countResult = countItems(menu_item_name, unit)
#         for total, itemName, itemUnit in countResult:
#             if total != 0:
#                 if unit == None:
#                     msg.append('%s total sold: %d' % (itemName, total))
#                 else:
#                     msg.append('%s - %s total sold: %d' % (itemName, unit, total))
#             else:
#                 msg.append('%s total sold: %d' % (menu_item_name, total))
#     message = '\n'.join(msg)
#     return message

def main():
    # cal()
    message = cal()
    print(message)
    # send_msg(message)
if __name__ == "__main__":
    main()
