# -*- coding: utf-8 -*-

import os
from datetime import datetime as dt

def to_date(timestamp):
  return dt.fromtimestamp(timestamp/1000)


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def dict_merge(dct, merge_dct):
  for k, v in merge_dct.iteritems():
    dct[k] += merge_dct[k]

def fix_values(value,deltas):
  result = [value]
  for d in deltas:
    result.append(result[-1]+d)
  return result


def parse_input_file(filename):
    import json
    with open(filename, 'r') as f:
      return json.load(f)

def is_valid_file(parser, arg):
  """
  Check if arg is a valid file that already exists on the file system.

  Parameters
  ----------
  parser : argparse object
  arg : str

  Returns
  -------
  arg
  """
  arg = os.path.abspath(arg)
  if not os.path.exists(arg):
    parser.error("The file %s does not exist!" % arg)
  else:
    return arg


