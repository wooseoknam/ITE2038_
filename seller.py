import time
import argparse
from helpers.connection import conn


def main(args):
    # TODO
    # you can edit the example code below whatever you want.
    # example code

    try:
        cur = conn.cursor()
        print("database is connected")
        if args.option == 'info':
            sql = "SELECT name, phone, local, domain FROM seller WHERE id=%s;"
            cur.execute(sql, args.id)
            rows = cur.fetchall()
            for row in rows:
                print(f'Name: {row[0]}')
                print(f'Phone Number: {row[1]}')
                print(f'email: {row[2]}@{row[3]}')
        elif args.option == 'update':
            sql = f"UPDATE seller SET {args.property[0]} = %s WHERE id=%s;"
            cur.execute(sql, (args.property[1], args.id))
            conn.commit()
            cur.close()

    except Exception as err:
        print(err)
    # end
    pass

if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    # TODO
    # you can edit the example code below whatever you want.
    # example code
    parser.add_argument("id", help="ID of Seller")
    parser.add_argument("option", help="options of seller")
    parser.add_argument("property", nargs=argparse.REMAINDER, help="Property to Change")
    # end

    args = parser.parse_args()
    main(args)
    print("Running Time: ", end="")
    print(time.time() - start)
