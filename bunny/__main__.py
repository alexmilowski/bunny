import argparse
from bunny import find_bundle
import json
import sys

parser = argparse.ArgumentParser(description='Bunny operation invocation')
parser.add_argument('-p','--parameter',nargs=2,help='A parameter value',action='append')
parser.add_argument('-c','--config',help='The bundle configuration.')
parser.add_argument('bundle',help='The bundle.')
parser.add_argument('operation',help='The client id for the authentication provider.')

args = parser.parse_args()

bundle = find_bundle(args.bundle)
if bundle is None:
   sys.stderr.write('Bundle {} not found'.format(args.bundle))

if args.config is not None:
   with open(args.config,'r') as data:
      bundle.configuration = json.load(data)

parameters = {}
if args.parameter is not None:
   for name,value in args.parameter:
      parameters[name] = value

response = bundle.invoke(args.operation,**parameters)
print(json.dumps(response,indent=3))