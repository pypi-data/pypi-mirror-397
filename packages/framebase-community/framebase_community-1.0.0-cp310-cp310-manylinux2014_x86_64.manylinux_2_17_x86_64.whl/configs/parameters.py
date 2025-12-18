import yaml,os,json
from typing import List, Optional, Dict, Union
from dotenv import load_dotenv  
from copy import deepcopy  
load_dotenv()  

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
    
class Parameters():
    '''
    Load yaml config
    '''
    def __init__(self, nested_parameters=None):
        load_dotenv(override=True)  
        self.params= deepcopy(nested_parameters) or {}
        self.name=self.params.get('name',None)
        self.type=self.params.get('type',None)
        if self.params.get('parameters'):
            self.keys=list(map(lambda x:x['name'],self.params['parameters']))
        else:
            self.keys=[]

    @classmethod
    def from_config(cls, config_name):
        config=read_yaml(os.path.join(os.path.dirname(__file__),config_name))
        return cls(config)

    def get(self,key,default_value=None):
        if key.upper() in os.environ:
            try:
                return json.loads(os.environ[key.upper()])
            except json.decoder.JSONDecodeError:
                try: 
                    return eval(os.environ[key.upper()])
                except:
                    return os.environ[key.upper()]

        if self.params.get('parameters'):
            target=list(filter(lambda x:x['name']==key,self.params['parameters']))
            if len(target):
                return target[0]['value']
            else:
                return default_value
        else:
            return default_value
    
    def get_all(self, exclude=None):
        exclude=exclude or []
        if self.params.get('parameters'):
            return [k for k in self.params['parameters'] if k['name'] not in exclude]
        else:
            return []
        
    def __len__(self):
        return len(self.params)

    def update(self, new_param):
        for p in new_param.params.get('parameters',[]):
            if 'parameters' in self.params:

                target=list(filter(lambda x:x['name']==p['name'],self.params['parameters']))
                if len(target):
                    target=target[0]
                    i=self.params['parameters'].index(target)
                    self.params['parameters'][i]=p
                else:
                    self.params['parameters'].append(p)
                    
                
        
        return self

    def __str__(self):
        return str(self.params)



if __name__=='__main__':

    #type 1
    config=read_yaml(os.path.join(os.path.dirname(__file__),'chains/conversation_chain.yaml'))
    parameters=Parameters(config)
    print(parameters.get_all())
    answer_priority = parameters.get('answer_priority')
    #type 2
    parameters=Parameters.from_config('service/service.yaml')
    print(parameters)
    print(parameters.get('redis_passwd'))