import configparser, json

params = {}

def get_params():
    """Retorna um dict com os parâmetros de entrada que define os campos onde as informações devem 
       ser extraidas do html.

    Returns:
        [dict]
    """
    FILE = './config.ini'
    
    file_config = configparser.ConfigParser()
    file_config.read(FILE)
    
    section_params = {}
    
    for section in file_config.sections():
        section_params = {}
        
        for key, value in file_config.items(section):
            section_params[key] = value

        params[section] = section_params

    return params