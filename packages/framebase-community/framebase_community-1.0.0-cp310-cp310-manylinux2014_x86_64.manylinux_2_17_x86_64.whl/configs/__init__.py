import os
from .parameters import Parameters, read_yaml
import pkg_resources

specs={}
for root,paths,files in os.walk(pkg_resources.resource_filename('configs','')):
    for path in paths:
        spec = {'parameters': []}
        for root, dirs, files in os.walk(pkg_resources.resource_filename('configs', path)):
            for file in files:
                if file.endswith('yaml'):
                    config = Parameters.from_config(os.path.join(path, file))
                    spec['parameters'].append({'name': config.name, 'value': config})
        specs[path]=Parameters(spec)
def get_configs(path='./'):
    
    return specs[path]

def get_and_reload_configs(module='./'):
    specs={}
    for root,paths,files in os.walk(pkg_resources.resource_filename('configs','')):
        for path in paths:
            spec = {'parameters': []}
            for root, dirs, files in os.walk(pkg_resources.resource_filename('configs', path)):
                for file in files:
                    if file.endswith('yaml'):
                        config = Parameters.from_config(os.path.join(path, file))
                        spec['parameters'].append({'name': config.name, 'value': config})
            specs[path]=Parameters(spec)
    return specs[module]