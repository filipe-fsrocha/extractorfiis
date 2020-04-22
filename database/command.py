from database.databaseconnection import DatatabaseConnection
from utils.constants import CONST

import logging.config, psycopg2, psycopg2.extras

logging.config.fileConfig(fname=(CONST.FILE_CONFIG_LOG), disable_existing_loggers=False)
logger = logging.getLogger('Command')

class Command:
    """Executa os comandos DML e DCL
    """

    def __init__(self):
        with DatatabaseConnection() as (conn):
            self.conn = conn

    def execute_command(self, command, params=None, _return=False, fetchone=False):
        """

        Arguments:
            command {str} -- query que será executada

        Keyword Arguments:
            params {dict} -- Parâmetros que complementa a query que será executada (default: {None})
            _return {bool} -- Define se o comando executado terá algum retorno (default: {False})
            fetchone {bool} -- Define se como select deverá retorna uma lista ou apenas um registro (default: {False})

        Returns:
            [dict] -- Retorna os resultados dos comandos select's executados
        """
        try:
            with self.conn.cursor(cursor_factory=(psycopg2.extras.DictCursor)) as (cursor):
                if params is None:
                    cursor.execute(command)
                    if _return:
                        result = cursor.fetchall()
                        return result
                else:
                    cursor.execute(command, params)
                    if _return:
                        if fetchone:
                            result = cursor.fetchone()
                        else:
                            result = cursor.fetchall()
                        return result
                    cursor.close()
        except (Exception, psycopg2.Error) as ex:
            logger.error('Erro whe executing the command: {0}'.format(cursor.query))
            logger.error('Error details: {0}'.format(ex))


    def select(self, command, params=None, fetchone=False):
        return self.execute_command(command, params, True, fetchone)


    def save(self, command, params):
        self.execute_command(command, params)


    def update(self, command, params=None):
        self.execute_command(command, params)


    def delete(self, command, params=None):
        self.execute_command(command, params)


    def commit(self):
        self.conn.commit()


    def rollback(self):
        self.conn.rollback()


    def close(self):
        self.conn.close()