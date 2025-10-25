from typing import List, Tuple, Dict

def fetch_tables(conn, schema: str = "public") -> List[str]:
    """
    Вернёт список таблиц в схеме.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema=%s AND table_type='BASE TABLE'
            ORDER BY table_name;
        """, (schema,))
        return [r[0] for r in cur.fetchall()]

def fetch_columns(conn, table: str, schema: str = "public") -> List[Tuple[str, str]]:
    """
    Вернёт список (column_name, data_type) для таблицы.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ordinal_position;
        """, (schema, table))
        return cur.fetchall()

def fetch_all_columns(conn, schema: str = "public") -> Dict[str, List[Tuple[str, str]]]:
    """
    Вернёт словарь: { table_name: [(column_name, data_type), ...], ... }
    """
    tables = fetch_tables(conn, schema)
    return {t: fetch_columns(conn, t, schema) for t in tables}
