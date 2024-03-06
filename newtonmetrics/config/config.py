import yaml


class Config(object):

    def __init__(self, path_to_config):
        self.path = path_to_config

    def read_config(self):
        try: 
            with open (self.path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            print( e)
        
        