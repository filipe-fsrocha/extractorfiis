from extractorfunds.extractorfiis import ExtractorFiis
from model.modelfii import ModelFii
from utils.constants import CONST

import uuid, datetime, logging.config

logging.config.fileConfig((CONST.FILE_CONFIG_LOG), disable_existing_loggers=False)
logger = logging.getLogger('DataSync')

class DataSync:

    def __init__(self):
        pass

    def data_sync(self):
        extractor = ExtractorFiis()
        
        complete_fii = {}
        
        start = datetime.datetime.now()
        logger.info('{} - Start job'.format(start.strftime('%Y-%m-%d %H:%M:%S')))
        
        for summary_fii in extractor.scrape_list_fiis():
            try:
                
                complete_fii = extractor.scrape_details_fii(summary_fii['symbol'])
                summary_fii.update({'id': '{}'.format(uuid.uuid4())})
                complete_fii.update({'sumary': summary_fii})
                ModelFii().save_or_update_complete_fii(complete_fii)
                
            except Exception as ex:
                logger.error('Fails to process the FII: {0} - Detail: {1}'.format(summary_fii['symbol'], ex))
                continue

        end = datetime.datetime.now()
        logger.info('{} - End job'.format(end.strftime('%Y-%m-%d %H:%M:%S')))
