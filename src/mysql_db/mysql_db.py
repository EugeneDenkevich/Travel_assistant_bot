import mysql.connector as sq
from itertools import chain
import bcrypt
# from checkboxes import regions, criteria, more_criteria


class StartConnection:

    def connect_db():
        global db, cur

        db = sq.connect(
            host = "localhost",
            user = "eugen",
            passwd="12345qwerty",
            port="3306"
        )

        cur = db.cursor()


    def mysql_start():
        StartConnection.connect_db()
        cur.execute("CREATE DATABASE IF NOT EXISTS farmstead_bot;")
        db.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS farmstead_bot.holder (\
                    id_holder BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                    first_name VARCHAR(255),\
                    last_name VARCHAR(255),\
                    contact_phone VARCHAR(255),\
                    contact_email VARCHAR(255),\
                    is_enter CHAR(2) NOT NULL DEFAULT 0,\
                    holder_id BIGINT,\
                    adm_password TEXT,\
                    holder_login VARCHAR(255) UNIQUE NOT NULL,\
                    current_writer_id BIGINT\
                    ) ENGINE = InnoDB;")
        cur.execute("CREATE TABLE IF NOT EXISTS farmstead_bot.farmstead (\
                    id_farmstead BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                    name VARCHAR(255) UNIQUE,\
                    address VARCHAR(255),\
                    photo TEXT,\
                    destination VARCHAR(255),\
                    rooms_number INT,\
                    services TEXT,\
                    price DECIMAL(20, 2),\
                    is_water_near CHAR(4),\
                    unique_services TEXT,\
                    phones TEXT,\
                    gps_number VARCHAR(255),\
                    website_link TEXT,\
                    popular VARCHAR(1) DEFAULT(1),\
                    holder_login VARCHAR(255),\
                    FOREIGN KEY (holder_login) REFERENCES holder (holder_login) ON DELETE CASCADE\
                    ) ENGINE = InnoDB;")
        cur.execute("CREATE TABLE IF NOT EXISTS farmstead_bot.customer (\
                    id_customer BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                    customer_login VARCHAR(255) UNIQUE NOT NULL,\
                    customer_password TEXT NOT NULL,\
                    is_entered INT NOT NULL DEFAULT 0,\
                    current_writer_id BIGINT\
                    ) ENGINE = InnoDB;")
        cur.execute("CREATE TABLE IF NOT EXISTS farmstead_bot.purchase (\
                    id_purchase BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                    farmstead_id BIGINT NOT NULL,\
                    start_date VARCHAR(100),\
                    finish_date VARCHAR(100),\
                    adults_number TINYINT,\
                    child_number TINYINT,\
                    rooms_number TINYINT,\
                    customer_id BIGINT,\
                    FOREIGN KEY (customer_id) REFERENCES customer (id_customer) ON DELETE CASCADE,\
                    FOREIGN KEY (farmstead_id) REFERENCES farmstead (id_farmstead) ON DELETE CASCADE\
                    ) ENGINE = InnoDB;")
        db.commit()

    
class BaseWorking:


    async def clear_db():
        pass


    async def add_new_farmstead(state):
        StartConnection.connect_db()
        async with state.proxy() as data:
            cur.execute("INSERT INTO farmstead_bot.farmstead (name, address, photo, destination, rooms_number, services,\
                price, is_water_near, unique_services, phones, gps_number, website_link, holder_login)\
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [data['name'], data['address'], data['photo'], data['destination'], data['rooms_number'],
                data['services'], data['price'], data['is_water_near'], data['unique_services'],
                data['contact_phones'], data['gps_number'], data['website_link'], data['holder_login']])
            db.commit()
            print("--- The data was added successfuly ---")


    async def get_user_ids():
        StartConnection.connect_db()
        cur.execute("SELECT holder_id FROM farmstead_bot.holder")
        ids = cur.fetchall()
        ids_list = []
        for i in ids:
            ids_list.append(*i)
        return ids_list


    async def get_farm_names():
        StartConnection.connect_db()
        cur.execute("SELECT name FROM farmstead_bot.farmstead")
        ids = cur.fetchall()
        ids_list = []
        for i in ids:
            ids_list.append(*i)
        return ids_list


    async def append_id_into_base(user_id):
        StartConnection.connect_db()
        l = []
        l.append(user_id)
        cur.execute("INSERT INTO farmstead_bot.holder (holder_id) VALUES (%s)", l)
        db.commit()


    async def get_assort():
        StartConnection.connect_db()
        cur.execute("SELECT name, address, photo FROM farmstead_bot.farmstead;")
        assort = cur.fetchall()
        return assort


    # --- Чекбокс:

    async def get_box_table(user_id, *fields):
        StartConnection.connect_db()
        try:
            cur.execute(f"CREATE TABLE IF NOT EXISTS farmstead_bot.checkbox_{user_id} (\
                        id BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,\
                        name VARCHAR(255),\
                        value VARCHAR(255) DEFAULT '⬜'\
                        );")
            if await BaseWorking.check_box(user_id) == []:
                for field in fields:
                    cur.execute(f"INSERT INTO farmstead_bot.checkbox_{user_id} (name) VALUES(%s)", [field])
                    db.commit()
            cur.execute(f"SELECT id, value, name FROM farmstead_bot.checkbox_{user_id};")
            res = cur.fetchall()
            return res
        except:
            return
            
    async def check_box(user_id) -> list:
        StartConnection.connect_db()
        try:
            cur.execute(f"SELECT name, value FROM farmstead_bot.checkbox_{user_id};")
            res = cur.fetchall()
            return res
        except Exception:
            return False
        

    async def drop_checkbox(user_id):
        StartConnection.connect_db()
        cur.execute(f"DROP TABLE IF EXISTS farmstead_bot.checkbox_{user_id}")
        db.commit()


    async def change_box(user_id, item):
        try:
            cur.execute(f"SELECT value FROM farmstead_bot.checkbox_{user_id} WHERE name='{item}';")
            res = str(*chain(*cur.fetchall()))
            if res == '⬜':
                cur.execute(f"UPDATE farmstead_bot.checkbox_{user_id} SET value='☑️' WHERE name='{item}';")
                db.commit()
            elif res == '☑️':
                cur.execute(f"UPDATE farmstead_bot.checkbox_{user_id} SET value='⬜' WHERE name='{item}';")
                db.commit()
        except:
            return


    async def get_id_by_name(item_id: str, user_id: int):
        item_id = item_id.split('_')[1]
        cur.execute(f"SELECT name FROM farmstead_bot.checkbox_{user_id} WHERE id={item_id}")
        res = cur.fetchall()
        return res


    async def set_customer_pass(client_pass, client_id):
        StartConnection.connect_db()
        cur.execute(f"INSERT INTO farmstead_bot.customer (customer_id, customer_password, is_entered) VALUES (%s, %s, 0)", [client_id, client_pass])
        db.commit()


    async def check_client_register(user_id):
        StartConnection.connect_db()
        cur.execute(f"SELECT customer_id FROM farmstead_bot.customer WHERE customer_id=%s", [user_id])
        res = cur.fetchall()
        if not res:
            return False
        else:
            return True


    async def check_client_password(login, password: str):
        StartConnection.connect_db()
        cur.execute("SELECT customer_password FROM farmstead_bot.customer WHERE customer_login=%s", [login])
        res = str(*chain(*cur.fetchall()))
        valid = bcrypt.checkpw(password.encode('utf-8'), res.encode('utf-8'))
        if valid:
            return True
        else:
            return False


    async def check_if_enter(user_id):
        StartConnection.connect_db()
        cur.execute(f"SELECT is_entered FROM farmstead_bot.customer WHERE customer_id=%s", [user_id])
        res = cur.fetchall()
        result = ''
        for i in res:
            for j in i:
                result += str(j)
        if result == '1':
            return True
        else:
            return False

    async def client_authorizate(user_id):
        StartConnection.connect_db()
        cur.execute(f"UPDATE farmstead_bot.customer SET is_entered=1 WHERE customer_id=%s", [user_id])
        db.commit()
        

    async def client_exit_from_account_change_db(user_id):
        StartConnection.connect_db()
        cur.execute(f"UPDATE farmstead_bot.customer SET is_entered=0 WHERE customer_id=%s", [user_id])
        db.commit()


    async def check_holder_password(holder_password: str, holder_login):
        StartConnection.connect_db()
        cur.execute("SELECT adm_password FROM farmstead_bot.holder WHERE holder_login=%s", [holder_login])
        hash: str = str(*chain(*cur.fetchall()))
        valid = bcrypt.checkpw(holder_password.encode('utf-8'), hash.encode('utf-8'))
        return valid
    

    async def check_if_admin_enter(current_holder_id):
        StartConnection.connect_db()
        cur.execute("SELECT is_enter FROM farmstead_bot.holder WHERE current_writer_id=%s", [current_holder_id])
        res = cur.fetchall()
        res = (list(chain(*res)))
        if res == []:
            return False
        else:
            return True if list(chain(*res))[0] == '1' else False if list(chain(*res))[0] == '0' else print('Error')


    async def get_holder_ids():
        StartConnection.connect_db()
        cur.execute("SELECT holder_id FROM farmstead_bot.holder")
        res = cur.fetchall()
        res = (list(chain(*res)))
        return res
        
        
    async def change_holder_enter(holder_login):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.holder SET is_enter=1 WHERE holder_login=%s", [holder_login])
        db.commit()

    
    async def change_holder_enter_exit(current_holder_id):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.holder SET is_enter=0 WHERE current_writer_id=%s", [current_holder_id])
        db.commit()


    async def create_new_holder(id, password: str, login):
        StartConnection.connect_db()
        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO farmstead_bot.holder (holder_id, adm_password, holder_login) VALUES (%s, %s, %s)",\
                    [id, hash.decode('utf-8'), login])
        db.commit()
        

    async def check_adm_login(holder_login):
        StartConnection.connect_db()
        cur.execute("SELECT holder_login FROM farmstead_bot.holder")
        res = cur.fetchall()
        return True if holder_login in list(chain(*res)) else False

    
    async def set_current_wtiter(holder_id, holder_login):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.holder SET current_writer_id=%s WHERE holder_login=%s", [holder_id, holder_login])
        db.commit()


    async def reset_current_writer(current_holder_id):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.holder SET current_writer_id=NULL WHERE current_writer_id=%s", [current_holder_id])
        db.commit()

    
    async def get_current_holder_login(holder_id):
        StartConnection.connect_db()
        cur.execute("SELECT holder_login FROM farmstead_bot.holder WHERE current_writer_id=%s", [holder_id])
        return str(*chain(*cur.fetchall()))


    def check_farm_name(name: str):
        StartConnection.connect_db()
        cur.execute("SELECT name FROM farmstead_bot.farmstead WHERE name=%s", [name])
        res = list(*cur.fetchall())
        if name.capitalize() not in res:
            return False
        else:
            return True
    

    async def add_purchase(data):
        StartConnection.connect_db()
        data = (dict(data))
        cur.execute("SELECT id_farmstead FROM farmstead_bot.farmstead WHERE name=%s",
                      [data['name'].capitalize().strip()])
        farm_id = int(*chain(*cur.fetchall()))
        cur.execute("INSERT INTO farmstead_bot.purchase (farmstead_id, start_date, finish_date, \
            adults_number, child_number, rooms_number) VALUES \
            (%s, %s, %s, %s, %s, %s);", [farm_id, data['start_date'], data['finish_date'],
            data['adults_number'], data['child_number'], data['rooms_number']])
        db.commit()


    async def check_client_login(login):
        StartConnection.connect_db()
        cur.execute("SELECT customer_login FROM farmstead_bot.customer;")
        res = cur.fetchall()
        return True if login not in list(chain(*res)) else False


    async def create_new_client(data):
        StartConnection.connect_db()
        password: str = data['password']
        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO farmstead_bot.customer (customer_login, customer_password)\
            VALUES (%s, %s);", [data['login'], hash.decode('utf-8')])
        db.commit()


    async def change_client_enter(login, user_id):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.customer SET is_entered=0, current_writer_id=NULL WHERE current_writer_id=%s", [user_id])
        cur.execute("UPDATE farmstead_bot.customer SET is_entered=1, current_writer_id=%s WHERE customer_login=%s", [user_id, login])
        db.commit() 


    async def check_client_state(login, user_id):
        StartConnection.connect_db()
        cur.execute("SELECT is_entered FROM farmstead_bot.customer WHERE customer_login=%s AND current_writer_id=%s", [login, user_id])
        res = cur.fetchall()
        if res == []:
            return False
        res = int(*chain(*res))
        if res == 0:
            return False
        if res == 1:
            return True


    async def get_client_login(current_writer_id):
        StartConnection.connect_db()
        cur.execute("SELECT customer_login FROM farmstead_bot.customer WHERE current_writer_id=%s",
                    [current_writer_id])
        res = cur.fetchall()
        return str(*chain(*res))


    async def logout_client(user_id):
        StartConnection.connect_db()
        cur.execute("UPDATE farmstead_bot.customer SET is_entered=0, current_writer_id=NULL WHERE current_writer_id=%s", [user_id])
        db.commit()


    async def find_client_id(user_id: str):
        StartConnection.connect_db()
        cur.execute("SELECT customer_login FROM farmstead_bot.customer WHERE current_writer_id=%s", [user_id])
        res = str(*chain(*cur.fetchall()))
        return (True, res) if res != '' else (False, res)


    async def get_popular() -> list:
        StartConnection.connect_db()
        cur.execute("SELECT photo, name, rooms_number FROM farmstead_bot.farmstead WHERE popular=1;")
        photo_path = cur.fetchall()
        return photo_path

    async def get_farm_by_criteria(user_id: int) -> list:
        StartConnection.connect_db()
        cur.execute("SELECT photo, name, rooms_number FROM farmstead_bot.farmstead WHERE popular=0;")
        photo_path = cur.fetchall()
        return photo_path
    

    async def get_criteria_table(user_id, data: dict) -> None:
        StartConnection.connect_db()
        cur.execute(f"DROP TABLE IF EXISTS farmstead_bot.searching_by_criteria_{user_id};")
        cur.execute(f"CREATE TABLE IF NOT EXISTS farmstead_bot.searching_by_criteria_{user_id} (" +
                    f"name VARCHAR(255), " +
                    f"value VARCHAR(255));")
        for k, v in data.items():
            cur.execute(f"INSERT INTO farmstead_bot.searching_by_criteria_{user_id} (name, value) VALUES ('{k}', '{v}')")
        db.commit()

    
    async def get_criteria(user_id: int) -> tuple:
        cur.execute(f"SELECT name, value FROM farmstead_bot.searching_by_criteria_{user_id};")
        res = cur.fetchall()
        return res
    

    async def update_criteria_table(user_id: int, data) -> None:
        cur.execute(f"INSERT INTO farmstead_bot.searching_by_criteria_{user_id}\
                    VALUES ('more_criteria', '{data}');")
        db.commit()


    async def drop_criteria(user_id: int) -> None:
        cur.execute(f"DROP TABLE IF EXISTS farmstead_bot.searching_by_criteria_{user_id};")
        db.commit()


if __name__ == "__main__":
    StartConnection.connect_db()
    print("\n---*** You've just connected to database from mysql_db.py ***---\n")