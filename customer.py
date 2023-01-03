import time
import argparse
from helpers.connection import conn
from datetime import datetime
import json

def main(args):
    # TODO

    try:
        cur = conn.cursor()
        print("database is connected")
        if args.option == 'info':
            if args.property:
                sql = f"SELECT {args.property[0]} FROM customer WHERE id = %s"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                print(f"{args.property[0]} of Customer {args.id}")
                for row in rows:
                    print(row)
            elif not args.property:
                sql = "SELECT * FROM customer WHERE id = %s;"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                print(f'Info of Customer {args.id}')
                for row in rows:
                    print(f'name: {row[1]}')
                    print(f'phone: {row[2]}')
                    print(f'local: {row[3]}')
                    print(f'domain: {row[4]}')
                    print(f'passwd: {row[5]}')
                    print(f'payments: {row[6]}')
                    print(f'lay/lng: {row[7]},', end=' ')
                    print(row[8])
        elif args.option == 'update':
            if args.property[1] == '-c':
                sql = f"UPDATE customer SET address = array_append(address, {args.property[2]}) WHERE id = %s;"
                cur.execute(sql, args.id)
                conn.commit()
            elif args.property[1] == '-e':
                sql = f"UPDATE customer SET address[%s] = {args.property[3]} WHERE id = %s;"
                cur.execute(sql, (args.property[2], args.id))
                conn.commit()
            elif args.property[1] == '-r':
                sql = f"UPDATE customer SET address = array_remove(address, address[%s]) WHERE id = %s;"
                cur.execute(sql, (args.property[2], args.id))
                conn.commit()
        elif args.option == 'pay':
            if not args.property:
                print('Index | Custome ID | Payment')
                print('=====================================================================')
                sql = "SELECT (jsonb_array_elements(payments))['data'] as data, (jsonb_array_elements(payments))['type'] as type from customer where id = %s"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                idx = 0
                for row in rows:
                    idx += 1
                    if row[1] == 'account':
                        print(f"    {idx}       {args.id}         bid={row[0]['bid']}, acc_num={row[0]['acc_num']}, type={row[1]}")
                    elif row[1] == 'card':
                        print(f"    {idx}       {args.id}         card_num={row[0]['card_num']}, type={row[1]}")
            elif args.property[0] == '--add-card':
                sql = "UPDATE customer SET payments = payments::jsonb || (\'{\"data\": {\"card_num\": %s}, \"type\":\"card\"}\')::jsonb WHERE id = %s;" % (args.property[1], args.id)
                cur.execute(sql)
                conn.commit()
            elif args.property[0] == '--add-account':
                sql = "UPDATE customer SET payments = payments::jsonb || (\'{\"data\": {\"bid\": %s, \"acc_num\": %s}, \"type\": \"account\"}\')::jsonb WHERE id = %s;" % (args.property[1], args.property[2], args.id)
                cur.execute(sql)
                conn.commit()
            elif args.property[0] == '-r':
                sql = f"update customer set payments = payments::jsonb - {int(args.property[1]) - 1} where id = %s;"
                cur.execute(sql, args.id)
                conn.commit()
        elif args.option == 'search':
            pass
        elif args.option == 'select':
            sql = f'UPDATE customer SET searching = {args.property[0]} WHERE id = %s;'
            cur.execute(sql, args.id)
            conn.commit()
        elif args.option == 'cart':
            if not args.property:
                searching = 'SELECT searching FROM customer WHERE id = %s;'
                cur.execute(searching, args.id)
                searching_id = int(cur.fetchone()[0])
                sql = f'SELECT menu FROM menu WHERE sid = (SELECT searching FROM customer WHERE id = %s);'
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                print(f'Menus of Store {searching_id}')
                print('-----------------------------------------')
                for i in range(len(rows)):
                    print(f'{i + 1}. {rows[i][0]}')
                print('-----------------------------------------')
            elif args.property[0] == '-c':
                for i in range(1, len(args.property)):
                    if (i % 2) == 1:
                        searching = 'SELECT searching FROM customer WHERE id = %s;'
                        cur.execute(searching, args.id)
                        searching_id = int(cur.fetchone()[0])
                        sql = f'SELECT menu FROM menu WHERE sid = (SELECT searching FROM customer WHERE id = %s);'
                        cur.execute(sql, args.id)
                        rows = cur.fetchall()
                        sql_ = f"INSERT INTO cart (cid, menu_id, menu_name, many, menu_info)" \
                               f"VALUES ({args.id}, {args.property[i]}, " \
                               f"%s, {args.property[i+1]}, %s);"
                        cur.execute(sql_, (rows[int(args.property[i]) - 1], [rows[int(args.property[i]) - 1], args.property[i+1]]))
                        conn.commit()
            elif args.property[0] == '-l':
                sql = f"SELECT menu_name FROM cart WHERE cid = {args.id}"
                cur.execute(sql)
                rows = cur.fetchall()
                print('Cart')
                for row in range(len(rows)):
                    print(f'{row + 1}. {list(rows[row])[0]}')
            elif args.property[0] == '-r':
                sql = f"DELETE FROM cart WHERE cid = {args.id}"
                cur.execute(sql)
                sql_ = f"UPDATE customer SET searching = NULL WHERE id = {args.id}"
                cur.execute(sql_)
                conn.commit()
            elif args.property[0] == '-p':
                menu_query = f"SELECT string_agg(menu_info, ',') AS menu_info FROM cart GROUP BY cid"
                cur.execute(menu_query, args.id)
                menu_info = cur.fetchone()
                payment_query = f"SELECT payments[{args.property[1]} - 1] FROM customer WHERE id = %s;"
                cur.execute(payment_query, args.id)
                pay = cur.fetchone()
                store_query = f'SELECT searching FROM customer WHERE id = %s'
                cur.execute(store_query, args.id)
                store = cur.fetchone()
                sql = f'INSERT INTO orders(sid, cid, menu_info, payment, ordert)' \
                      f'VALUES (%s, %s, %s, %s, %s)'
                cur.execute(sql, (list(store)[0], args.id, list(menu_info)[0], json.dumps(pay[0]), datetime.now()))
                conn.commit()
        elif args.option == 'list':
            if not args.property:
                store_query = "SELECT sname FROM store WHERE id = (SELECT searching FROM customer WHERE id = %s)"
                cur.execute(store_query, args.id)
                store_name = cur.fetchall()
                sql = "SELECT ordert, status FROM orders WHERE cid = %s"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                for i in range(len(rows)):
                    print('Store name   |   Order time                  |   Delivery status')
                    print('-----------------------------------------------------------------')
                    print(list(store_name[i])[0] + '    ' + str(rows[i][0]) + '        ' + rows[i][1])
            elif (args.property[0] == '-w') or (args.property[0] == '--waiting'):
                store_query = "SELECT sname FROM store WHERE id = (SELECT searching FROM customer WHERE id = %s)"
                cur.execute(store_query, args.id)
                store_name = cur.fetchall()
                sql = "SELECT ordert, status FROM orders WHERE cid = %s"
                cur.execute(sql, args.id)
                rows = cur.fetchall()
                for i in range(len(rows)):
                    if rows[i][1] == 'delivering':
                        print('Store name   |   Order time                  |   Delivery status')
                        print('-----------------------------------------------------------------')
                        print(list(store_name[i])[0] + '    ' + str(rows[i][0]) + '        ' + rows[i][1])
    except Exception as err:
        print(err)
    pass


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    # TODO
    parser.add_argument("id", help="ID of seller")
    parser.add_argument("option", help="options of seller")
    parser.add_argument("property", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
