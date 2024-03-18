import oracledb

#Create a connection pool
pool = oracledb.create_pool(user='ADMIN', password='Capstone1234;', dsn='(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gc1ee84d2900e16_capstone_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))')

def get_user(user_id):
    #Establish a database connection from the pool
   
    with pool.acquire() as connection:
        #Perform database operations
        with connection.cursor() as cursor:
            #Execute query to retrieve the user
            cursor.execute("SELECT id, username FROM Users WHERE id = :id", [user_id])
            user_row = cursor.fetchone()
            if user_row:
                return {
                    'id': user_row[0],
                    'username': user_row[1]
                }
            else:
                return None

import oracledb

def get_user_stocks(user_id):
    stocks_list = []
    # Assuming `pool` is your OracleDB connection pool defined elsewhere
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            # Use a dictionary to pass named parameters for clarity and safety
            query = "SELECT symbol, quantity FROM Stocks WHERE user_id = :user_id"
            cursor.execute(query, user_id=user_id)  # Pass `user_id` as a named parameter
            for stock_row in cursor:
                # Assuming `stock_symbol` and `quantity` are the correct column names, adjust if necessary
                stocks_list.append({
                    'symbol': stock_row[0],  # Adjusted from 'stock_id' to 'stock_symbol'
                    'quantity': stock_row[1]  # Adjusted from 'progress' to 'quantity' for clarity
                })
    return stocks_list


