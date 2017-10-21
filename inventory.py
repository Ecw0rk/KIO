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
            # sql = "select menu_item_name, unit from menu"
            sql = "select menu_item_name, unit, inventory, mid from menu join inventory on menu.in_id = inventory.in_id"
            cursor.execute(sql)
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
                sql = "select count(*), menu_item_name, unit from history_order_detail where menu_item_name = %s and unit = %s" \
                      "and order_time between %s and %s"
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
                sql = "select count(*), menu_item_name, unit from history_order_detail where menu_item_name = %s" \
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
    for menu_item_name, unit, inventory, mid in items:
        # print(menu_item_name, unit, type(inventory), type(mid))
        countResult = countItems(menu_item_name, unit)
        for weekSold, itemName, itemUnit in countResult:
            inventory = inventory - weekSold
            if weekSold != 0:
                if unit == None:
                    msg.append('%s sold: %d remain %d' % (menu_item_name, weekSold, inventory))
                else:
                    msg.append('%s %s sold: %d remain %d' % (menu_item_name, unit, weekSold, inventory))
            else:
                if unit == None:
                    msg.append('%s sold: %d remain %d' % (menu_item_name, weekSold, inventory))
                else:
                    msg.append('%s %s sold: %d remain %d' % (menu_item_name, unit, weekSold, inventory))
        # with conn.cursor() as cursor:
        #     sql = "update inventory join menu on inventory.in_id = menu.in_id set inventory=%s where menu.mid = %s"
        #     cursor.execute(sql, (inventory, mid))
            # conn.commit()
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
