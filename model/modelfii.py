from database.command import Command
from utils.constants import CONST
import uuid, database.query as query, logging.config

logging.config.fileConfig((CONST.FILE_CONFIG_LOG), disable_existing_loggers=False)
logger = logging.getLogger('ModelFii')

class ModelFii(Command):
    
    
    def find_by_id(self, _id):
        return self.select('select * from fii where id=%(id)s', {'id': _id}, fetchone=True)


    def find_by_symbol(self, symbol):
        return self.select('select * from fii where symbol=%(symbol)s', {'symbol': symbol}, fetchone=True)


    def save_or_update_complete_fii(self, complete_fii):
        """

        Arguments:
            complete_fii {dict} -- Dados completo do FII (Fundo de Investimento imobiliário)
        """
        
        params = self.__include_relationship_id(complete_fii)
        symbol = params['sumary']['symbol']
        
        try:
            if not self.__exists_fii(symbol):
                self.save(query.generate_query('fii'), params['sumary'])
                
                for key in params:
                    if key != 'sumary':
                        if key != 'assets':
                            if params[key]:
                                self.save(query.generate_query(self.__mapper_table(key)), params[key])
                    if key == 'assets':
                        for item in range(0, len(params[key])):
                            self.save(query.generate_query(self.__mapper_table(key)), params[key][item])

            else:
                find_fii = self.find_by_symbol(symbol)
                
                if find_fii:
                    for key in params:
                        if key == 'sumary':
                            sql = query.generate_query(self.__mapper_table(key), 'UPDATE', {'field':'id',  'bind':'id'})
                            self.update(sql, params[key])
                            
                        elif key == 'dividends':
                            if params[key]:
                                if self.__exists_detail_fii(self.__mapper_table(key), {'fiiId': find_fii['id']}) is None:
                                    params[key]['id'] = self.__nex_id()
                                    self.save(query.generate_query(self.__mapper_table(key)), params[key])
                                else:
                                    sql = query.generate_query(self.__mapper_table(key), 'UPDATE', {'field':'fii_id',  'bind':'fiiId'})
                                    self.update(sql, params[key])
                                    
                        elif key == 'assets':
                            if params[key]:
                                self.__remove_assets({'fiiId': find_fii['id']})
                                
                                for item in range(0, len(params[key])):
                                    self.save(query.generate_query(self.__mapper_table(key)), params[key][item])
                            else:
                                for item in range(0, len(params[key])):
                                    self.save(query.generate_query(self.__mapper_table(key)), params[key][item])
                        else:
                            sql = query.generate_query(self.__mapper_table(key), 'UPDATE', {'field':'fii_id',  'bind':'fiiId'})
                            self.update(sql, params[key])
            
            self.commit()
            logger.info("FII: {} inserido e/ou atualizado com sucesso.".format(symbol))
        except Exception as ex:
            self.rollback()
            logger.error('Error when trying to save the FII: {0} - Detail: {1}'.format(symbol, ex))

    def __include_relationship_id(self, complete_fii):
        """Gera as chaves de relacionamento entre o resumo do FII (Fundo de Investimento imobiliário) com as demais informações 
        complementares [indicatores, informações básicas, dividendos, ativos].
        
        if fii exists:
            remove as keys id's do dict[complete_fii] mantendo apenas a key [fii_id] de relacionamento e ela é atualizada com o 
            o id do fii encontrado.
        else:
            gera novos id's 

        Arguments:
            complete_fii {dict} -- 

        Returns:
            [dict] -- Retorna o dict com as chaves [id, fiiId] atualizadas
        """
        
        remove_id = False
        fii_id = complete_fii['sumary']['id']
        symbol = complete_fii['sumary']['symbol']
        
        if self.__exists_fii(symbol):
            fii_id = self.find_by_symbol(symbol)['id']
            complete_fii['sumary']['id'] = fii_id
            remove_id = True

        for key in complete_fii:
            if key != 'assets':
                if key != 'sumary':
                    if complete_fii[key]:
                        complete_fii[key]['id'] = '{}'.format(uuid.uuid4())
                        complete_fii[key]['fiiId'] = fii_id
                        
            if key == 'assets':
                for item in range(0, len(complete_fii[key])):
                    complete_fii[key][item]['id'] = '{}'.format(uuid.uuid4())
                    complete_fii[key][item]['fiiId'] = fii_id

        if remove_id:
            for key in complete_fii:
                if key != 'assets' and key != 'sumary':
                    if 'id' in complete_fii[key].keys():
                        del complete_fii[key]['id']

        return complete_fii

    def __mapper_table(self, key):
        tables = {
            'sumary':'fii', 
            'indicators':'indicators', 
            'basicInfo':'basic_information', 
            'dividends':'dividends', 
            'assets':'assets_fiis'
        }
        
        return tables.get(key)

    def __exists_fii(self, symbol):
        exists = True
        
        if not self.find_by_symbol(symbol):
            exists = False
            
        return exists

    def __exists_detail_fii(self, table, _filter):
        sql = 'select id, fii_id from {} where fii_id=%(fiiId)s'.format(table)
        find = self.select(sql, _filter, fetchone=True)
        
        if not find:
            return None
        else:
            return find


    def __remove_assets(self, fii_id):
        self.delete('delete from assets_fiis where fii_id=%(fiiId)s', fii_id)


    def __nex_id(self):
        return '{}'.format(uuid.uuid4())