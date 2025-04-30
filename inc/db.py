import sqlite3

DB_FILE = './inc/database.db'

# usage: new_db("table_name", [("name1", "type1"), ("name2", "type2")])
def new_db(table, columns):
    if isinstance(columns, list):
        column_defs = ', '.join(f'{name} {type}' for name, type in columns)
        query = f'CREATE TABLE IF NOT EXISTS {table} ({column_defs})'

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        conn.close()
    else:
        raise ValueError("columns must be a list.")

# usage: table_exists("table_name") returns true:false
def table_exists(table_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# usage: db_insert(table, [("key1", "value1"), ("key2", "value2")])
def db_insert(table, keys, values):
    if isinstance(keys, list) and isinstance(values, list):
        if len(keys) != len(values):
            raise ValueError("Key and value lists must be the same length.")
        
        columns = ', '.join(keys)
        placeholders = ', '.join('?' for _ in keys)
        query = f'INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})'

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Fix: Pass the values list directly, not wrapped in another list
        c.execute(query, values)  # This is the correct usage
        conn.commit()
        conn.close()
    else:
        raise ValueError("keys and values must be lists.")

# usage: db_read(table, [("key1", "key1")])
def db_read(table, keys):
    if not isinstance(keys, list):
        raise ValueError("keys must be a list.")

    # If keys indicate wildcard or all rows
    if keys == ["*:*"] or keys == []:
        query = f"SELECT * FROM {table}"
        params = []
    else:
        where_clauses = []
        params = []
        for condition in keys:
            if ":" not in condition:
                raise ValueError(f"Invalid key condition: {condition}")
            column, value = condition.split(":", 1)
            if value == "*":
                where_clauses.append(f"{column} IS NOT NULL")
            else:
                where_clauses.append(f"{column} = ?")
                params.append(value)
        where_sql = " AND ".join(where_clauses)
        query = f"SELECT * FROM {table} WHERE {where_sql}"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchall()
    conn.close()

    return result if result else None

# Read multiple entries, support multiple keys
def db_get(table, keys):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    values = []
    for key in keys:
        k, v = key.split(":", 1)  # Split key:value
        c.execute(f'SELECT cookies FROM {table} WHERE guild_id = ? AND user_id = ?', (v, k))
        result = c.fetchone()
        values.append(result)
    
    conn.close()
    return values

# Update multiple entries, with checks
def db_update(table, keys, values):
    if isinstance(keys, list) and isinstance(values, list):
        if len(values) != 1:
            raise ValueError("There must be exactly one value to update.")
        
        # Prepare the column names and their corresponding values
        column_values = []
        where_clauses = []
        
        for key in keys:
            column, value = key.split(":", 1)  # Split the key into column name and value
            where_clauses.append(f"{column} = ?")
            column_values.append(value)
        
        # The SET clause for updating cookies
        query = f'UPDATE {table} SET cookies = ? WHERE ' + ' AND '.join(where_clauses)

        # Execute the query
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, [values[0]] + column_values)  # First value is the new cookies value, then the keys
        conn.commit()
        conn.close()
    else:
        raise ValueError("keys and values must be lists.")

# Delete entries based on multiple keys
def db_delete(table, keys):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if isinstance(keys, list):
        placeholders = ','.join('?' for _ in keys)
        c.execute(f'DELETE FROM {table} WHERE key IN ({placeholders})', keys)
    else:
        c.execute(f'DELETE FROM {table} WHERE key = ?', (keys,))

    conn.commit()
    conn.close()
