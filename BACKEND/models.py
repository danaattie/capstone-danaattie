import oracledb

pool = oracledb.create_pool(user='ADMIN', password='Cpastone1234;', dsn='(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gc1ee84d2900e16_capstone_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))')

def get_user(user_id):
    #establish a database connection from the pool
    with pool.acquire() as connection:
        #perform database operations
        with connection.cursor() as cursor:
            #execute query to retrieve the user
            cursor.execute("SELECT id, username FROM Users WHERE id = :id", [user_id])
            user_row = cursor.fetchone()
            if user_row:
                return {
                    'id': user_row[0],
                    'username': user_row[1]
                }
            else:
                return None

def get_user_stocks(user_id):
    stocks_list = []
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, user_id, episode_id, progress FROM Stocks WHERE user_id = :user_id", [user_id])
            for stock_row in cursor:
                stocks_list.append({
                    'id': stock_row[0],
                    'user_id': stock_row[1],
                    'episode_id': stock_row[2],
                    'progress': stock_row[3]
                })
    return stocks_list
