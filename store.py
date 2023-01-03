import time
import argparse
from helpers.connection import conn
from geopy import distance
import math
from datetime import datetime

def main(args):
    # TODO
    try:
        cur = conn.cursor()
        print("database is connected")
        if args.option == 'info':
            sql = "SELECT address, sname, lat, lng, phone_nums, schedules FROM store WHERE id=%s;"
            cur.execute(sql, args.id)
            rows = cur.fetchall()
            for row in rows:
                print(f'Address: {row[0]}')
                print(f'Store Name: {row[1]}')
                print(f'Location: {row[2]}, {row[3]}')
                print(f'Phone Number: {row[4]}')
                for i in row[5]:
                    print(f'Schedule: {i}')
        elif args.option == 'menu':
            if args.property[0] == '--list':
                sql = "SELECT sid, menu.id, menu.menu FROM menu WHERE menu.sid=%s;"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                print()
                print(f'Menu of store {rows[0][0]}')
                print('---------------------------------------')
                for row in range(len(rows)):
                    print(f'{row + 1}. Menu ID: {rows[row][1]}, Name: {rows[row][2]}')
                print('---------------------------------------')
            elif args.property[0] == '--add':
                sql = "INSERT INTO menu (menu, sid) VALUES (%s, %s);"
                cur.execute(sql, (args.property[1].strip("'"), args.id))
                conn.commit()
                cur.close()
        elif args.option == 'order':
            if args.property[0] == '--update':
                store_location_query = f'SELECT lat, lng FROM store WHERE id = %s'
                cur.execute(store_location_query, args.id)
                store_location = cur.fetchone()
                did_query = f"SELECT id FROM delivery d WHERE stock <= 4 " \
                            f"ORDER BY power(({store_location[0]} - d.lat), 2) + power(({store_location[1]} - d.lng), 2) LIMIT 1;"
                cur.execute(did_query)
                did = cur.fetchone()
                # set_delivery_query = f"UPDATE orders SET did = {did}, status = 'delivering' " \
                #                      f"WHERE id = (SELECT id FROM orders WHERE sid = {args.id} ORDER BY id {args.property[1]}"
                set_delivery_query = f"UPDATE orders SET did = %s, status = 'delivering' from (select ROW_NUMBER() OVER() as rn, menu " \
                                     f"FROM (select menu from menu where sid = {args.id} order by id)as x) as y where rn = {args.property[2]}"
                cur.execute(set_delivery_query, did)
                conn.commit()
            elif args.property[0] == '--list':
                if len(args.property) == 1:
                    sql = 'SELECT o.sid, o.cid, o.menu_info, o.payment, o.ordert, o.delivert, c.phone, o.status ' \
                          'FROM orders o, customer c WHERE sid = %s and c.id = o.cid'
                    cur.execute(sql, args.id)
                    rows = cur.fetchall()
                    print('Orders')
                    for row in rows:
                        print(f'Store ID: {row[0]}')
                        print(f'Customer ID: {row[1]}')
                        print(f'Menu: {row[2]}')
                        print(f'Payment: {row[3]}')
                        print(f'Otime: {row[4]}')
                        print(f'Dtime: {row[5]}')
                        print(f'cphone: {row[6]}')
                        print(f'status: {row[7]}')
                elif len(args.property) == 2:
                    sql = "SELECT id FROM orders WHERE orders.status = 'delivering' and sid = %s"
                    cur.execute(sql, args.id)
                    rows = cur.fetchall()
                    print(f'Delivering for Store {args.id}')
                    for row in rows:
                        print(f'Order: {list(row)[0]}')
        elif args.option == 'stat':
            start_date_query = "SELECT to_timestamp(%s, 'YYYY/MM/DD')"
            cur.execute(start_date_query, (args.property[0], ))
            start_date = cur.fetchone()
            start_date_string = list(start_date)[0].strftime('%Y/%m/%d')
            finish_date = start_date_string[:-2] + str(int(start_date_string[-2:]) + int(args.property[1]))
            sql = f"select ordert::date as Date, count(*) FROM orders " \
                  f"WHERE sid = %s and ordert::date >= %s::date and ordert::date < %s::date " \
                  f"group by ordert::date"
            cur.execute(sql, (args.id, start_date, finish_date))
            rows = cur.fetchall()
            print("    Date    |    Orders")
            for row in rows:
                print(f'{row[0]}        {row[1]}')
        elif args.option == 'search':
            sql = 'SELECT o.cid, c.name FROM orders o ' \
                  'FULL OUTER JOIN customer c ON o.cid=c.id WHERE o.sid = %s'
            cur.execute(sql, args.id)
            rows = cur.fetchall()
            print("Customer ID    |    Customer name")
            print('---------------------------------------')
            for row in rows:
                print(f'     {row[0]}         |    {row[1]}')

    except Exception as err:
        print(err)
    # end
    pass


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    # TODO
    parser.add_argument("id", help="ID of Seller")
    parser.add_argument("option", help="options of seller")
    parser.add_argument("property", nargs=argparse.REMAINDER, help="Property to Change")

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
