'''Database interaction'''

from typing import Any
import psycopg2 as _psycopg2
from psycopg2 import sql

class PostgreSQLConnection():
    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

    def __enter__(self) -> 'PostgreSQLConnection':
        self._connection = _psycopg2.connect(
            database=self._database,
            port=self._port,
            host=self._host,
            user=self._user,
            password=self._password
        )

        self._cursor = self._connection.cursor()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._cursor.close()
        self._connection.close()

    def commit(self) -> None:
        self._connection.commit()

    def cancel(self) -> None:
        self._connection.cancel()

    def execute(self, query: sql.Composed, data: dict[str, Any] | None = None, commit: bool = True) -> None:
        self._cursor.execute(query, data)

        if commit:
            self.commit()
    
    def fetch_one(self) -> tuple[Any, ...] | None:
        return self._cursor.fetchone()
    
    def fetch_all(self) -> list[tuple[Any, ...]]:
        return self._cursor.fetchall()
    
    def set_schema(self, schema: str) -> None:
        query = sql.SQL('SET search_path TO {schema}').format(schema=sql.Identifier(schema))
 
        self.execute(query, { 'schema': schema })

    def create_schema(self, schema: str) -> None:
        query = sql.SQL('CREATE SCHEMA IF NOT EXISTS {schema}').format(schema=sql.Identifier(schema))
 
        self.execute(query, { 'schema': schema })

    def delete_schema(self, schema: str) -> None:
        query = sql.SQL('DROP SCHEMA IF EXISTS {schema} CASCADE').format(schema=sql.Identifier(schema))
 
        self.execute(query, { 'schema': schema })

    def insert(self, schema: str, table: str, data: dict[str, Any], return_fields: list[str] = []) -> list[tuple[str, Any]] | None:
        '''
        Inserts a row into a specified table within a PostgreSQL database.

        :param schema: The schema name where the table resides.
        :param table: The name of the table to insert data into.
        :param data: A dictionary where keys are column names and values are the data to insert.
        :param return_fields: A list of fields to return after the insert. Defaults to an empty list.

        :returns: If `return_fields` is specified, returns a tuple containing the values of the requested fields. 
                    Otherwise, returns None.

        :notes: 
            - The `data` dictionary keys must match the column names of the table.
        '''
        
        if len(return_fields) > 0:
            base_query = 'INSERT INTO {schema}.{table}({fields}) VALUES({values}) RETURNING {return_fields}'
        else:
            base_query = 'INSERT INTO {schema}.{table}({fields}) VALUES({values})'

        query = sql.SQL(base_query).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table),
            fields=sql.SQL(',').join([sql.Identifier(key) for key in data.keys()]),
            values=sql.SQL(',').join([sql.Placeholder(key) for key in data.keys()]),
            return_fields=sql.SQL(',').join([sql.Identifier(key) for key in return_fields])
        )

        if len(return_fields) > 0:
            self.execute(query, data)
            return self.fetch_all()
        return self.execute(query, data)


class PostgreSQL:
    '''Connection with a PostgreSQL database'''
    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:     
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

    def connect(self) -> PostgreSQLConnection:
        return PostgreSQLConnection(self._host, self._port, self._database, self._user, self._password)

    def get_query_string(self, query: sql.SQL) -> str:
        with self.connect() as c:
            return query.as_string(c._connection)
        
    def execute(self, query: sql.Composed, data: dict[str, Any] | None = None, commit: bool = True) -> None:
        with self.connect() as c:
            c.execute(query, data, commit=commit)

    def execute_and_fetch(self, query: sql.Composed, data: dict[str, Any] | None = None) -> list[tuple[Any, ...]]:
        with self.connect() as c:
            c.execute(query, data)
            return c.fetch_all()


    def insert(self, schema: str, table: str, data: dict[str, Any], return_fields: list[str] = []) -> list[tuple[str, Any]] | None:
        '''
        Inserts a row into a specified table within a PostgreSQL database.

        :param schema: The schema name where the table resides.
        :param table: The name of the table to insert data into.
        :param data: A dictionary where keys are column names and values are the data to insert.
        :param return_fields: A list of fields to return after the insert. Defaults to an empty list.

        :returns: If `return_fields` is specified, returns a tuple containing the values of the requested fields. 
                    Otherwise, returns None.

        :notes: 
            - The `data` dictionary keys must match the column names of the table.
        '''
        
        with self.connect() as c:
            result = c.insert(schema, table, data, return_fields)
            c.commit()

            return result
