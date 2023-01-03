import time
import argparse
from helpers.connection import conn


def main(args):
    # TODO
    try:
        cur = conn.cursor()
        print("database is connected")
        if not args.property:
            sql = f"SELECT id, sid, cid FROM orders WHERE did = {args.id} and status = 'delivering';"
            cur.execute(sql)
            rows = cur.fetchall()
            print("Order id | Store id | Customer id | status")
            print('---------------------------------------------------------')
            for row in rows:
                print(f'    {row[0]}         {row[1]}           {row[2]}         delivering')
        elif args.property[0] == '-e':
            sql = f"UPDATE orders SET status = 'delivered', delivert = now() at time zone 'Asia/Seoul' WHERE did = %s and id = %s"
            cur.execute(sql, (args.id, args.property[1]))
            conn.commit()
        elif args.property[0] == '-a':
            sql = f'SELECT status, id FROM orders WHERE did = {args.id}'
            cur.execute(sql)
            rows = cur.fetchall()
            print("Delivery status | Order id")
            print('----------------------------')
            for row in rows:
                print(f'{row[0]}           {row[1]}')
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
