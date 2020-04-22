"""
    Extractorfiis nasce com o objetivo de extrair as informações de fundos imobiliários do website https://www.fundsexplorer.com.br/, as 
    informações são extraídas usando webscraping e armazenadas no banco de dados PostgreSQL. Após manter as informações armazenadas e 
    sincronizadas uma api poderá ser disponibilizadas para consultar as informaçẽos completas dos FII's.
"""

__author__ = "Filipe Rocha"
__license__ = "GNU General Public License"
__version__ = "1.0.0"
__maintainer__ = "Filipe Rocha"
__email__ = "filipe.fsrocha@gmail.com"
__status__ = "Prototype"


from datasync.datasync import DataSync

import schedule, time, datetime


def main():
    """
        Execução agendada nos horários de abertatura e encerramento das negociações na B3
    """
    week_day = int(datetime.datetime.today().strftime('%w'))
    
    if week_day > 0 and week_day < 6:
        schedule.every().day.at("10:00").do(DataSync().data_sync)
        schedule.every().day.at("17:55").do(DataSync().data_sync)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()