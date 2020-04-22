from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from utils.constants import CONST

import re
import configparser
import logging.config

import config.config as params


logging.config.fileConfig(CONST.FILE_CONFIG_LOG, disable_existing_loggers=False)
logger = logging.getLogger("ExtractorFiis")
        
class ExtractorFiis:
    """Realiza a extração das informações dos FII's (Fundos de investimentos imobiliários) das paginas .html
    
    """
    
    HEADER = {'User-Agent': 'Mozilla/5.0 (X11)'}
    
    def __init__(self):
        self.params = params.get_params()
        
        
    def scrape_list_fiis(self):
        """Gera uma lista com os resumos do FII's [symbol, name, administrator]

        Returns:
            [list] -- Retorna uma lista com todos os FII's encontrados.
        """
        
        logger.info("Start load list of FII's")
        
        req = Request(self.create_url(), headers=self.HEADER)
        webpage = urlopen(req).read()
        bsHtml = BeautifulSoup(webpage, 'html.parser')
        
        # Identifica quais classes (css) ou tags (html) deve ser usadas para extrair as informações do .html
        params_list_fiis = self.params['listFiis']
        list_fiis = []
        
        for fiis in bsHtml.find_all('div', class_='item'):
            try:
                
                fii_item = {
                    "symbol": fiis.find(class_=params_list_fiis['css.class.symbol']).next,
                    "name": fiis.find(class_=params_list_fiis['css.class.name']).next,
                    "administrator": str(fiis.find(class_=params_list_fiis['css.class.admin']).next).strip()
                }
                
                list_fiis.append(fii_item)
                logger.debug("FII: {} was successfully collected.".format(fii_item['symbol']))
                
            except Exception as ex:
                logger.error("Error when extracting information from the HTML template: {}".format(ex.args))
                continue
            
        logger.info("Finshed load of list FII's.")
        return list_fiis
    
    
    def scrape_details_fii(self, symbol):
        """Após a coleta da lista de FII's essa metódo coleta as informaçẽos detalhadas.

        Arguments:
            symbol {str} -- Código da ação do FII

        Returns:
            [dict] -- Retorna um dicionário com os detalhes completos do FII informado.
        """
        
        req = Request(self.create_url(symbol), headers=self.HEADER)
        webpage = urlopen(req).read()
        bsHtml = BeautifulSoup(webpage, 'html.parser')
        
        # Identifica quais classes (css) ou tags (html) deve ser usadas para extrair as informações do .htlm
        params_detail_fii = self.params['financialDetail']
        params_basic_infos = self.params['infoBasic']
        params_dividends_fii = self.params['dividends']
        params_fund_actives_fii = self.params['assets']
        
        detail_fii = {}
        indicators_fii = {}
        basic_infos_fii = {}
        dividends_fii = {}
        assets_fii = []
        
        try:
            
            stock_price = bsHtml.find('div', id=params_detail_fii['css.id.stock.price'])
            price = str(self.regex_replace(r"R\$\s|\%", "", stock_price.find(class_=params_detail_fii['css.class.price']).next)).strip()
            percentage = str(self.regex_replace(r"R\$\s|\%", "", stock_price.find(class_=params_detail_fii['css.class.percentage']).next)).strip()
            
            pos_key = 0
            
            if bsHtml.find_all('section', id=params_detail_fii['css.id.indicators']) is not None:
                default_value_indicators = lambda value: -999 if (value == "N/A") else value
                indicator = bsHtml.find('section', id=params_detail_fii['css.id.indicators'])
                
                for find_indicator in indicator.find_all('div', class_=params_detail_fii['css.class.carousel.cell']):
                    key_indicator = self.generate_keys("keysIndicator", "{}".format(pos_key))
                    value_indicator = str(find_indicator.find(class_=params_detail_fii['css.class.indicator.value']).next).strip()
                    
                    if not value_indicator.__contains__("bi") or not value_indicator.__contains__("mi"):
                        value_indicator = value_indicator.replace(".","").replace(",",".")
                        
                    indicators_fii[key_indicator] = default_value_indicators(self.regex_replace(r"R\$\s|\%", "", value_indicator))
                    pos_key += 1
                
                indicators_fii['price'] = default_value_indicators(price.replace(".", "").replace(",","."))
                indicators_fii['percentage'] = default_value_indicators(percentage.replace(".","").replace(",","."))
            
            if bsHtml.find_all('section', id=params_basic_infos['css.id.basic.infos']) is not None:
                pos_key = 0   
                basic_info = bsHtml.find('section', id=params_basic_infos['css.id.basic.infos'])
            
                for info in basic_info.find_all('li'):
                    key_basic_info = self.generate_keys("keysBasicInfo", "{}".format(pos_key))
                    basic_infos_fii[key_basic_info] = str(info.find(class_=params_basic_infos['css.class.description']).next).strip()
                    pos_key += 1
            
            if bsHtml.find('section', id=params_dividends_fii['css.id.dividends']) is not None:
                dividends = bsHtml.find('section', id=params_dividends_fii['css.id.dividends'])
                dividends_table_tbody = dividends.find('tbody')
                list_dividends = []

                if dividends_table_tbody is not None:
                    for line_dividend in dividends_table_tbody.find_all('tr'):
                        item = {}
                        pos_key = 0

                        for col_dividend in line_dividend.find_all('td'):
                            key_dividend = self.generate_keys("keyDividends", "{}".format(pos_key))
                            item[key_dividend] = col_dividend.next
                            pos_key += 1

                        list_dividends.append(item)

                    merge_dividends = {}
                    for key in list_dividends[0]:
                        merge_dividends[key] = list_dividends[0][key] + "|" + list_dividends[1][key]

                    dividends_fii = merge_dividends
            
            if bsHtml.find('section', id=params_fund_actives_fii['css.id.actives']) is not None:
                fund_items = bsHtml.find('div', id=params_fund_actives_fii['css.id.fund.actives.items'])
                
                for fund in fund_items.find_all('div', class_=params_fund_actives_fii['css.class.item']):
                    pos_key = 0
                    assets_item_address = {} 
                    assets_item_address['name'] = fund.find(class_=params_fund_actives_fii['css.class.title']).next
                    
                    for address in fund.find_all('li'):
                        (key, value) = str(address.text).split(":")
                        key_address = self.generate_keys("keyAddress", "{}".format(pos_key))
                        assets_item_address[key_address] = str(value).strip()
                        
                        pos_key += 1
                    
                    assets_fii.append(assets_item_address)
                        
            detail_fii['indicators'] = indicators_fii
            detail_fii['basicInfo'] = basic_infos_fii
            detail_fii['dividends'] = dividends_fii
            detail_fii['assets'] = assets_fii

            return detail_fii
        
        except Exception as ex:
            logger.error("Error when extracting information FII ({0}): {1}".format(symbol, ex))
            print(ex)
            
    
    def create_url(self, query=None):
        url = self.params['fundsExplorer']['url']
        
        if query is not None:
            url = "{0}/{1}".format(url, query)
        
        return url
    
    
    def regex_replace(self, regex, replace, var):
        if var is not None and type(var) is not int:
            return re.sub(regex, replace, var)
        return var
            

    def is_equals_ignore_case(self, var1, var2):
        return str(var1).lower() == str(var2).lower()
    
    
    def generate_keys(self, section, key):
        """Obtem as chaves que irá armezar as informações dos FII's no dict

        Arguments:
            section {str} -- Recebe a seção que contém as chaves (localizado no arquivo config.ini)
            key {int} -- Recebe as chaves da seção informada para obter a nova chave

        Returns:
            [str] -- A nova chave encontrada no arquivo config.ini
        """
        params_keys = self.params[section]
        return params_keys[key]