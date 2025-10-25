import psycopg2
from psycopg2 import sql

class Data:
    def __init__(self):
        super(Data, self).__init__()
        self.connection = None
        self.is_connected = False

    # ------------------- CONNECT / SCHEMA -------------------

    def create_connection(self):
        try:
            self.connection = psycopg2.connect(
                host='localhost',
                database='demo',
                user='postgres',
                password='Nn1234ksdfsire123!',
                port=5432
            )
            self.is_connected = True
            print("PostgreSQL connection established!")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            return False

    def create_tables(self):
        if not self.is_connected or self.connection is None:
            return False
        try:
            cursor = self.connection.cursor()

            enum_query = """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'expense_category') THEN
                    CREATE TYPE expense_category AS ENUM ('Образование', 'Здоровье', 'Учеба');
                END IF;
            END $$;
            """
            cursor.execute(enum_query)

            users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGSERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE
            )
            """
            cursor.execute(users_table_query)

            expenses_table_query = """
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name TEXT,
                category expense_category,
                date VARCHAR(20),
                price REAL,
                description VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
            cursor.execute(expenses_table_query)

            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO users (username) VALUES (%s)", ("default_user",))

            self.connection.commit()
            cursor.close()
            print("Tables created successfully with ENUM category!")
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def connect_to_database(self):
        if self.create_connection():
            if self.create_tables():
                print("Database setup completed successfully!")
                return True
        return False

    # ------------------- EXEC HELPERS -------------------

    def execute_query_with_params(self, sql_query, query_values=None):
        if not self.is_connected or self.connection is None:
            print("No database connection!")
            return None
        try:
            cursor = self.connection.cursor()
            if query_values:
                cursor.execute(sql_query, query_values)
            else:
                cursor.execute(sql_query)
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Query error: {e}")
            if self.connection:
                self.connection.rollback()
            return None

    # ------------------- APP QUERIES -------------------

    def add_new_transaction_query(self, name, category, date, price, description):
        if not self.is_connected or self.connection is None:
            print("Cannot add transaction - no database connection")
            return False
        try:
            sql_query = """
            INSERT INTO expenses (user_id, name, category, date, price, description)
            VALUES ((SELECT user_id FROM users LIMIT 1), %s, %s, %s, %s, %s)
            """
            cursor = self.execute_query_with_params(sql_query, [name, category, date, price, description])
            if cursor:
                cursor.close()
                print("Transaction added successfully!")
                return True
            return False
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False

    def get_all_expenses(self):
        if not self.is_connected or self.connection is None:
            return []
        try:
            sql_query = """
            SELECT expense_id, name, user_id, category, date, price, description
            FROM expenses
            ORDER BY expense_id DESC
            """
            cursor = self.execute_query_with_params(sql_query)
            if cursor:
                results = cursor.fetchall()
                cursor.close()
                return results
            return []
        except Exception as e:
            print(f"Error fetching expenses: {e}")
            return []

    # ---- ТЕКСТОВЫЙ ПОИСК (LIKE / ILIKE / POSIX) ----
    def search_expenses(self, column: str, operator: str, pattern: str):
        """
        column  ∈ {name, category, date, description}
        operator ∈ {LIKE, ILIKE, ~, ~*, !~, !~*}
        pattern — строка шаблона (например, '%уч%' или '^\d{2}\.\d{2}\.\d{4}$')
        Для ENUM 'category' и на всякий случай для остальных — приводим к ::text.
        """
        if not self.is_connected or self.connection is None:
            raise RuntimeError("Нет подключения к базе данных.")

        allowed_cols = {"name", "category", "date", "description"}
        allowed_ops  = {"LIKE", "ILIKE", "~", "~*", "!~", "!~*"}

        if column not in allowed_cols:
            raise ValueError("Недопустимая колонка для поиска.")
        if operator not in allowed_ops:
            raise ValueError("Недопустимый оператор поиска.")

        col_sql = f'("{column}")::text'  # безопасно для ENUM и любых типов

        sql_query = f"""
        SELECT expense_id, name, user_id, category, date, price, description
        FROM expenses
        WHERE {col_sql} {operator} %s
        ORDER BY expense_id DESC
        """
        cursor = self.execute_query_with_params(sql_query, [pattern])
        if not cursor:
            return []
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # ---- агрегаты для карточек ----
    def get_total(self, column, filter=None, value=None):
        if not self.is_connected or self.connection is None:
            return '0'
        sql_query = f"SELECT SUM({column}) FROM expenses"
        query_values = []
        if filter is not None and value is not None:
            sql_query += f" WHERE {filter} = %s"
            query_values.append(value)
        cursor = self.execute_query_with_params(sql_query, query_values)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            if result and result[0] is not None:
                return str(result[0])
        return '0'

    def total_education(self):
        return self.get_total(column="price", filter="category", value="Образование")

    def total_health(self):
        return self.get_total(column="price", filter="category", value="Здоровье")

    def total_study(self):
        return self.get_total(column="price", filter="category", value="Учеба")

    def total_price(self):
        return self.get_total(column="price")

    def __del__(self):
        if self.connection:
            try:
                self.connection.close()
                print("Database connection closed.")
            except Exception:
                pass
