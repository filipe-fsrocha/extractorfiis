from utils.constants import CONST

import psycopg2 as pg 
import psycopg2.extras, configparser, logging.config

logging.config.fileConfig(fname=(CONST.FILE_CONFIG_LOG), disable_existing_loggers=False)
logger = logging.getLogger('Connection')

class DatatabaseConnection:
    
    conn = None

    def __init__(self):
        self.dbconfig = configparser.ConfigParser()
        self.dbconfig.read(CONST.FILE_CONFIG_PARAMS)


    def __enter__(self):
        try:
            
            self.conn = psycopg2.connect(dbname=(self.dbconfig.get('db', 'dbname')),
            user=(self.dbconfig.get('db', 'user')),
            host=(self.dbconfig.get('db', 'host')),
            password=(self.dbconfig.get('db', 'password')),
            port=(self.dbconfig.get('db', 'port')),
            options=('-c search_path=' + self.dbconfig.get('db', 'schema')))
            
            return self.conn
        except (Exception, psycopg2.Error) as error:
            logger.error('Error while connecting to PostgreSQL: {0}'.format(error))


    def __exit__(self, exc_type, exc_val, exc_tb):
        pass