from typing import List, Tuple, Dict


def fetch_tables(conn, schema: str = 'public') -> List[str]:
    """
    Вернуть список таблиц в указанной схеме.
    Например: ['expenses', 'users']
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """, (schema,))
        rows = cur.fetchall() or []
    return [r[0] for r in rows]


def fetch_columns(conn, table: str, schema: str = 'public') -> List[Tuple[str, str]]:
    """
    Вернуть список колонок таблицы:
    [('expense_id','bigint'), ('name','character varying'), ('category','expense_category'), ...]
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        rows = cur.fetchall() or []
    return rows


def fetch_all_columns(conn, schema: str = 'public') -> Dict[str, List[Tuple[str, str]]]:
    """
    Собрать структуру:
    {
        'expenses': [('expense_id','bigint'), ('name','character varying'), ...],
        'users':    [('user_id','bigint'), ('username','character varying'), ...]
    }
    """
    result: Dict[str, List[Tuple[str, str]]] = {}
    tables = fetch_tables(conn, schema)
    for t in tables:
        result[t] = fetch_columns(conn, t, schema)
    return result
