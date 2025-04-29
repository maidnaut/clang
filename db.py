import sqlite3

# Initialize the database (run once at the start)
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    # Create a table if it doesn't already exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Create a new entry (insert data into the database)
def db_create(key, value):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    c.execute('INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)', (key, value))

    conn.commit()
    conn.close()

# Read an entry from the database
def db_read(key):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    c.execute('SELECT value FROM data WHERE key = ?', (key,))
    result = c.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None  # If no result is found

# Update an entry in the database
def db_update(key, value):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    c.execute('UPDATE data SET value = ? WHERE key = ?', (value, key))

    conn.commit()
    conn.close()

# Delete an entry from the database
def db_delete(key):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()

    c.execute('DELETE FROM data WHERE key = ?', (key,))

    conn.commit()
    conn.close()