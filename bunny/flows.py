import json
import time
from datetime import date,timedelta
import importlib
import os

def load_context(context):
   types = {}
   for name,definition in context.items():
      ptype = definition.get('@type')
      if ptype is not None:
         types[name] = ptype
   return types

class Bundle:
   def __init__(self,data,base_dir=None,configuration=None):
      self.data = data
      self.context = self.data.get('@context',{})
      self.types = load_context(self.context)
      self.base_dir = base_dir
      self.configuration = configuration

   def find(self,name):
      return self.data.get(name)

   def invoke(self,name,**data):
      operation = self.find(name)
      if operation is None:
         raise ValueError('Operation {name} is not defined.'.format(name=name))
      for typed in self.types:
         value = data.get(typed)
         if value is None:
            continue
         ptype = self.types.get(typed)
         if ptype=='xsd:date':
            pass
         elif ptype=='xsd:dateTime':
            value = value[:value.index('T')]
         else:
            continue
         on = time.strptime(value,'%Y-%m-%d')
         request_day = date(on.tm_year,on.tm_mon,on.tm_mday)
         preceding_day = request_day - timedelta(days=1)
         following_day = request_day + timedelta(days=1)
         data[typed+'_Y'] = request_day.year
         data[typed+'_y'] = request_day.year%1000
         data[typed+'_m'] = request_day.month
         data[typed+'_d'] = request_day.day
         data[typed+'_preceding_Y'] = preceding_day.year
         data[typed+'_preceding_y'] = preceding_day.year%1000
         data[typed+'_preceding_m'] = preceding_day.month
         data[typed+'_preceding_d'] = preceding_day.day
         data[typed+'_preceding'] = '{Y:04}-{m:02}-{d:02}'.format(Y=preceding_day.year,m=preceding_day.month,d=preceding_day.day)
         data[typed+'_following_Y'] = following_day.year
         data[typed+'_following_y'] = following_day.year%1000
         data[typed+'_following_m'] = following_day.month
         data[typed+'_following_d'] = following_day.day
         data[typed+'_following'] = '{Y:04}-{m:02}-{d:02}'.format(Y=following_day.year,m=following_day.month,d=following_day.day)

      data['base_dir'] = self.base_dir

      if self.configuration is not None:
         values = self.configuration.get('values')
         if values is not None:
            data = {**data, **values}

      arguments = []

      for spec in operation['arguments']:
         if type(spec)==str:
            try:
               arguments.append(spec.format(**data))
            except KeyError as k:
               raise ValueError('Undefined key {k} used in argument: {a}'.format(k=k.args[0],a=spec))
         elif spec.get('@type')=='ArgumentSet':
            set_name = spec.get('name')
            sets = self.configuration.get('arguments') if self.configuration is not None else None
            if sets is not None:
               params = sets.get(set_name)
               if params is not None:
                  for param in params:
                     try:
                        arguments.append(param.format(**data))
                     except KeyError as k:
                        raise ValueError('Undefined key {k} used in argument: {a}'.format(k=k.args[0],a=param))


      script = importlib.import_module(operation['script'])

      result = script.main(arguments)

      return result

def find_bundle(*search,**defaults):
   for path in search:
      location = path.format(**defaults)
      try:
         with open(location,'r') as data:
            wf = json.load(data)
            base_dir,_ = os.path.split(location)
            return Bundle(wf,base_dir=base_dir)
      except FileNotFoundError as err:
         pass
   return None
