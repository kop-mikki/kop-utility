import pyodbc
from typing import List, Any, Dict


class SQLServerConnection(object):
    """Connection class for a sql database
    Args:
        server (str, optional): The server ip or path to the server. Defaults to None.
        driver (str, optional): The driver the opperating system can use to connect to the sql. Defaults to None.
        database (str, optional): The name of the Database. Defaults to None.
    """

    def __init__(self, server: str = None,  driver: str = None, database: str = None):
        """Initializes connection to a database

        Args:
            server (str, optional): The server ip or path to the server. Defaults to None.
            driver (str, optional): The driver the opperating system can use to connect to the sql. Defaults to None.
            database (str, optional): The name of the Database. Defaults to None.
        """
        connection_string = ('DRIVER={};'
                             'SERVER={};'
                             'DATABASE={};'
                             'Trusted_Connection=yes;').format(driver, server, database)

        conn = pyodbc.connect(connection_string, autocommit = True)
        self.cursor = conn.cursor()

    def update(self, table: str, update_columns: List[str],
               condition_columns: List[str], values: List[Any]):
        """Executes Update statement in the connected database

        Args:
            table (str): Name of the table being updated
            update_columns (List[str]): List of names of the columns that are being updated
            condition_columns (List[str]): List of conditions
            values (List[Any]): List of the new values
        """
        update_columns_query = ' = ?, '.join(update_columns)

        condition_columns_query = ' = ? and '.join(condition_columns)

        self.cursor.execute("""UPDATE {} 
                               SET {} = ? 
                               WHERE {} = ?""".format(
            table, update_columns_query, condition_columns_query), values)
        
    def insert(self, table: str, columns: List[str], values: List):
        """Executes Insert statement in the connected database

        Args:
            table (str): Name of the table being inserted into
            columns (List[str]): List of names of the columns that are being inserted into
            values (List): List of the values
        """
        table = '[{}]'.format(table)
        header = ', '.join(['[{}]'.format(x) for x in columns])
        parameters = ', '.join(['?']*len(columns))

        self.cursor.execute('insert into {} ({}) values({})'.format(table, header, parameters), values)

    def select(self, table: str, columns: List[str] = None):
        """Executes Select statement in the connected database

        Args:
            table (str): Name of the table being selected
            columns (List[str], optional): List of the columns being selected. Defaults to None.

        Returns:        
             List[Dict[str, Any]]: Returns a list of the rows returned from the database
        """
        table = '[{}]'.format(table)
        header = '*'
        if columns is not None:
            header = ', '.join(['[{}]'.format(x) for x in columns])

        self.cursor.execute('select {} from {}'.format(header, table))
        result = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]

        return [dict(zip(columns, x)) for x in result]
