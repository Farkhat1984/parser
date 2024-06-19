import sqlite3
from datetime import datetime

def create_connection(db_file):
    """ Создать соединение с базой данных SQLite, указанной в db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """ Создать таблицы в базе данных """
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS бухгалтерия (
            ID INTEGER PRIMARY KEY,
            Тема TEXT NOT NULL,
            Содержание TEXT NOT NULL,
            Дата TEXT NOT NULL,
            Изображения TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS розница (
            ID INTEGER PRIMARY KEY,
            Тема TEXT NOT NULL,
            Содержание TEXT NOT NULL,
            Дата TEXT NOT NULL,
            Изображения TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS управление_торговлей (
            ID INTEGER PRIMARY KEY,
            Тема TEXT NOT NULL,
            Содержание TEXT NOT NULL,
            Дата TEXT NOT NULL,
            Изображения TEXT
        );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def add_item(conn, table_name, тема, содержание, дата, изображения):
    """ Добавление новой записи в таблицу """
    sql = f''' INSERT INTO {table_name}(Тема,Содержание,Дата,Изображения)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (тема, содержание, дата, изображения))
    conn.commit()
    return cur.lastrowid

def update_item(conn, table_name, id, тема, содержание, дата, изображения):
    """ Обновление информации о записи """
    sql = f''' UPDATE {table_name}
              SET Тема = ? ,
                  Содержание = ? ,
                  Дата = ? ,
                  Изображения = ?
              WHERE ID = ?'''
    cur = conn.cursor()
    cur.execute(sql, (тема, содержание, дата, изображения, id))
    conn.commit()

def delete_item(conn, table_name, id):
    """ Удаление записи по ID """
    sql = f'DELETE FROM {table_name} WHERE ID=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

def find_item_by_any(conn, table_name, search_query):
    """ Поиск записи по любому полю """
    sql = f"""SELECT * FROM {table_name} WHERE 
              Тема LIKE ? OR 
              Содержание LIKE ? OR 
              Дата LIKE ? OR
              Изображения LIKE ?"""
    cur = conn.cursor()
    cur.execute(sql, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    rows = cur.fetchall()
    return rows

# Пример использования
conn = create_connection("mydatabase.db")
create_table(conn)
# Добавить запись в таблицу бухгалтерия
add_item(conn, 'бухгалтерия', 'Новая тема', 'Описание содержания', datetime.now().strftime("%Y-%m-%d"), 'http://example.com/image.jpg')
# Обновить запись в таблице бухгалтерия
update_item(conn, 'бухгалтерия', 1, 'Обновленная тема', 'Новое описание', datetime.now().strftime("%Y-%m-%d"), 'http://example.com/newimage.jpg')
# Найти записи, соответствующие запросу
items = find_item_by_any(conn, 'бухгалтерия', 'Обновленная тема')
print(items)
# Удалить запись
delete_item(conn, 'бухгалтерия', 1)
