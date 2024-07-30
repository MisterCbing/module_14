import sqlite3

connection = sqlite3.connect("products.db")

cursor = connection.cursor()

def initiate_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
    )
    ''')

    farm = ['', 'ПАПАЗОЛ', 'ВЫПИВОН', 'ЗАГРУСТИН', 'БЫЛЗОЛ']

    for i in range(1,5):
        cursor.execute("INSERT INTO Products(title, description, price) VALUES (?, ?, ?)",
                    (f"{farm[i]}", f"описание{i}", i * 100))


def get_all_products():
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')
    res = cursor.fetchall()
    connection.close()
    return res

# initiate_db()
# connection.commit()

