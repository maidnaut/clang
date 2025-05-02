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

# Delete a whole table
def drop_table(table):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()

# usage: table_exists("table_name") returns true:false
def table_exists(table_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# usage: db_insert("table_name", [("name1", "type1"), ("name2", "type2")])
def db_insert(table, keys, values):
    if isinstance(keys, list) and isinstance(values, list):
        if len(keys) != len(values):
            raise ValueError("Key and value lists must be the same length.")
        
        columns = ', '.join(keys)
        placeholders = ', '.join('?' for _ in keys)
        query = f'INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})'

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute(query, values)
        conn.commit()
        conn.close()
    else:
        raise ValueError("keys and values must be lists.")

# usage: db_read(table, [("key1", "key1")])
def db_read(table, conditions=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    values = []

    if conditions:
        if conditions == ["*:*"]:
            query = f"SELECT * FROM {table}"
        else:
            clauses = []
            for cond in conditions:
                if cond == "*:*":
                    continue  # skip this invalid clause
                if ':' in cond:
                    key, val = cond.split(':', 1)
                    if val == '*':
                        clauses.append(f"{key} IS NOT NULL")
                    else:
                        clauses.append(f"{key} = ?")
                        values.append(val)

            where_clause = ' AND '.join(clauses)
            query = f"SELECT * FROM {table} WHERE {where_clause}"
    else:
        query = f"SELECT * FROM {table}"

    c.execute(query, values)
    rows = c.fetchall()
    conn.close()
    return rows if rows else []


# usage: db_update("table", [f"guild_id:{guild_id}"], [("rate", rate)])
def db_update(table, conditions, updates):
    set_clause = ", ".join(f"{field} = ?" for field, _ in updates)
    where_parts = []
    where_values = []
    
    for cond in conditions:
        if ':' in cond:
            col, val = cond.split(':', 1)
            where_parts.append(f"{col} = ?")
            where_values.append(val)
    
    query = f"UPDATE {table} SET {set_clause} WHERE {' AND '.join(where_parts)}"
    values = [val for _, val in updates] + where_values
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, values)
    conn.commit()
    conn.close()

# usage: db_delete(table, [("key":"value"}])
def db_delete(table, keys, values):
    if isinstance(keys, list) and isinstance(values, list):
        if len(keys) != len(values):
            raise ValueError("Key and value lists must be the same length.")
        
        conditions = ' AND '.join(f"{k} = ?" for k in keys)
        query = f"DELETE FROM {table} WHERE {conditions}"

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, values)
        conn.commit()
        conn.close()
    else:
        raise ValueError("keys and values must be lists.")