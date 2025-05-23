import sqlite3

def init_db():
    conn = sqlite3.connect('discounts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price_was REAL,
            price_is REAL,
            difference REAL,
            discount REAL,
            link TEXT,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_discount(item):
    conn = sqlite3.connect('discounts.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO discounts (name, price_was, price_is, difference, discount, link, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        item['name'], item['priceWas'], item['priceIs'],
        item['difference'], item['discount'], item['link'], item['image']
    ))
    conn.commit()
    conn.close()

def get_top_discounts(min_discount=30, limit=5):
    conn = sqlite3.connect('discounts.db')
    c = conn.cursor()
    c.execute('''
        SELECT name, discount, link FROM discounts
        WHERE discount >= ?
        ORDER BY discount DESC
        LIMIT ?
    ''', (min_discount, limit))
    results = c.fetchall()
    conn.close()
    return results
