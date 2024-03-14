CREATE TABLE Users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50),
    password VARCHAR2(50),
    CONSTRAINT users_pk PRIMARY KEY (user_id)   --making id the primary key
);

CREATE TABLE Stocks (
    stock_id NUMBER PRIMARY KEY,
    user_id NUMBER,
    symbol VARCHAR2(50),
    quantity NUMBER
);

ALTER TABLE Stocks
ADD CONSTRAINT fk_user FOREIGN KEY (user_id)
    REFERENCES Users (user_id);

INSERT INTO Users (username, password) 
VALUES ('testUser', 'testPass');    -- the password should be hashed for user's protection
commit;

SELECT * from Users
SELECT * from Stocks

-- stocks for user

INSERT INTO Stocks (user_id, stock_id, symbol, quantity)
VALUES ((SELECT user_id FROM Users WHERE username = 'testUser'), 1, 'AAPL', 11);

INSERT INTO Stocks (user_id, stock_id, symbol, quantity)
VALUES ((SELECT user_id FROM Users WHERE username = 'testUser'), 2, 'MSFT', 22);

INSERT INTO Stocks (user_id, stock_id, symbol, quantity)
VALUES ((SELECT user_id FROM Users WHERE username = 'testUser'), 3, 'NVDA', 33);

INSERT INTO Stocks (user_id, stock_id,symbol, quantity)
VALUES ((SELECT user_id FROM Users WHERE username = 'testUser'), 4, 'GOOGL', 44);

INSERT INTO Stocks (user_id, stock_id, symbol, quantity)
VALUES ((SELECT user_id FROM Users WHERE username = 'testUser'), 5, 'AMZN', 55);
commit;

BEGIN -- here will be the interaction from our server:
--Publish MYBACKEND tables for REST access. 
    ORDS.ENABLE_OBJECT(p_enabled => TRUE,
                       p_schema => 'Capstone',
                       p_object => 'Users',
                       p_object_type => 'TABLE',
                       p_object_alias => 'users',
                       p_auto_rest_auth => FALSE);
    commit;
END;
/

BEGIN
    ORDS.ENABLE_OBJECT(p_enabled => TRUE,
                       p_schema => 'Capstone',
                       p_object => 'Stocks',
                       p_object_type => 'TABLE',
                       p_object_alias => 'stocks',
                       p_auto_rest_auth => FALSE);
    commit;
END;
/
--Rest api endpoint for fetching user and password:

BEGIN
  ORDS.define_service(
    p_module_name    => 'user check',
    p_base_path      => 'users/',
    p_pattern        => ':username/:password/',
    p_method         => 'GET',
    p_source_type    => ORDS.source_type_collection_feed,
    p_source         => 'SELECT username, password 
                         FROM Users u
                         WHERE u.username = :username AND u.password = :password', 
    p_items_per_page => 10
  );
  commit;
END;
/

--in this endpoint i need to fetch the portfolio composition for a given user:
--REMEMBER THIS WILL GIVE AN EMPTY 'items' LIST IF THE USERNAME IS NOT FOUND
BEGIN
  ORDS.define_service(
    p_module_name    => 'user_stocks',
    p_base_path      => 'user_stocks/',
    p_pattern        => ':username/',
    p_method         => 'GET',
    p_source_type    => ORDS.source_type_collection_feed,
    p_source         => 'SELECT s.stock_id, s.quantity 
                         FROM Users u JOIN CAPSTONE.STOCKS s ON u.USER_ID = s.USER_ID 
                         WHERE u.USERNAME = :username',  --this query will get the stock composition
    p_items_per_page => 10
  );
  commit;
END;
/