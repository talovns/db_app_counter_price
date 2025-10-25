from typing import List, Tuple
import psycopg2

def execute_sql(conn, sql_text: str) -> Tuple[List[str], List[Tuple]]:
    """
    Выполнить произвольный SELECT/SHOW/EXPLAIN и вернуть (headers, rows).
    Делает ROLLBACK при ошибке, чтобы соединение не зависало в aborted.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text)
            headers = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall() if cur.description else []
            return headers, rows
    except psycopg2.Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise RuntimeError(f"Ошибка выполнения SQL: {e.pgerror or e}") from e

def execute_ddl(conn, sql_text: str) -> None:
    """
    Выполнить DDL/ALTER/CREATE/DROP. Коммитит, делает роллбек при ошибке.
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"Ошибка изменения схемы: {e.pgerror or e}") from e
