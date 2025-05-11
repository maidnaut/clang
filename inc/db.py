import sqlite3, re

DB_FILE = './inc/database.db'

# usage: new_db("table_name", [("name1", "type1"), ("name2", "type2")])
def new_db(table, columns):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

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

# usage: table_exists("table") returns true:false
def table_exists(table):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# usage: db_insert("table_name", [("name1", "type1"), ("name2", "type2")])
def db_insert(table, keys, values):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

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

# usage: db_remove("table_name", [("name1", "type1"), ("name2", "type2")])
def db_remove(table, keys, values):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

    if isinstance(keys, list) and isinstance(values, list):
        if len(keys) != len(values):
            raise ValueError("Key and value lists must be the same length.")
        
        conditions = ' AND '.join(f"{key} = ?" for key in keys)
        query = f'DELETE FROM {table} WHERE {conditions}'

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, values)
        conn.commit()
        conn.close()
    else:
        raise ValueError("keys and values must be lists.")

# usage: db_read(table, [("key1", "key1")])
def db_read(table, conditions=None):
    import re
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    values = []
    query = f"SELECT * FROM {table}"

    if conditions:
        if conditions == ["*:*"]:
            pass  # no WHERE clause needed
        else:
            clauses = []
            for cond in conditions:
                if cond == "*:*":
                    continue

                if ':' not in cond:
                    raise ValueError(f"Malformed condition: {cond}")

                key, val = cond.split(':', 1)

                if val == '*':
                    clauses.append(f"{key} IS NOT NULL")
                else:
                    # Match optional operator and value
                    match = re.match(r'^([<>]=?|=)?(.+)$', val)
                    if not match:
                        raise ValueError(f"Invalid condition value: {val}")

                    operator, real_val = match.groups()
                    operator = operator or '='
                    if operator not in ['=', '<', '>', '<=', '>=']:
                        raise ValueError(f"Unsupported operator: {operator}")

                    clauses.append(f"{key} {operator} ?")
                    values.append(real_val)

            where_clause = ' AND '.join(clauses)
            query += f" WHERE {where_clause}"

    c.execute(query, values)
    rows = c.fetchall()
    conn.close()
    return rows if rows else []



# usage: db_update("table", [f"guild_id:{guild_id}"], [("rate", rate)])
def db_update(table, conditions, updates):
    if not isinstance(table, str) or not table.isidentifier():
        raise ValueError("Invalid table name.")

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