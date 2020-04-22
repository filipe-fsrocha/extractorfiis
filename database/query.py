import json

def generate_fields_table(table_name, _type=None):
    """

    Arguments:
        table_name {str} -- Tabela para gerar os campos

    Keyword Arguments:
        _type {str} -- Identificar se será gerado binds de insert ou update (default: {None})

    Returns:
        {dict} -- Retorna os campos é os bind para montar o comando sql
    
    Input:
        {
            "tableName": "table",
            "fields": ["field_1", "field_2", "field_3"],
            "binds": ["field1", "field2", "field3"]
        }
    
    Output:
        {
            "fields": "field_1, field_2, field_3",
            "binds": "field1, field2, field3
        }
        
    """
   
    tables_config = json.loads(open('tables.json').read())
    
    params = {}
    fields = []
    binds = []
    
    if len(tables_config['tables']) > 0:
        for table in tables_config['tables']:
            if table['tableName'] == table_name:
                for field in table['fields']:
                    if _type is None:
                        fields.append(field)
                    else:
                        fields.append('{}=bind'.format(field))

                for bind in table['binds']:
                    bind = '%({})s'.format(bind)
                    binds.append(bind)

        if _type is not None:
            del fields[0]
            del binds[0]
            for i in range(0, len(fields)):
                fields[i] = str(fields[i]).replace('bind', binds[i])

        params['fields'] = ', '.join(fields)
        params['binds'] = ', '.join(binds)
        return params
    else:
        return params


def generate_query(table, _type=None, _filter=None):
    query = None
    command_sql = None
    
    if _type is None:
        query = generate_fields_table(table)
        command_sql = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table, query['fields'], query['binds'])
    else:
        fields = lambda fields: fields + ', update_at=now()' if table == 'fii' else fields
        query = generate_fields_table(table, _type)
        command_sql = 'UPDATE {0} SET {1} '.format(table, fields(query['fields']))
        
        if _filter is not None:
            command_sql = command_sql + 'WHERE {0}=%({1})s'.format(_filter['field'], _filter['bind'])
            
    return command_sql