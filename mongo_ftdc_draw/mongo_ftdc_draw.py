# -*- coding: utf-8 -*-

"""FTDC drawer"""

import pkg_resources
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os, numpy as np
import matplotlib.pyplot as plt
import matplotlib
from .utils import *

plt.rc('font', size=7)  
plt.rc('lines', linewidth=0.8)
plt.rc('lines', color='r')



CONFIG = {}


def draw_plot(data, data_hidden, plot_count, output_filename):
  figsize = len(CONFIG)*2
  fig = plt.figure(figsize=(8, 2))

  true_start = to_date(data_hidden['start'][0])
  true_end = to_date(data_hidden['end'][-1])

  index = 1
  tmp_merged = False
  tmp_merged_names = []
  for group_key in sorted(data.keys()):
      index +=1
      ax = fig.add_subplot(plot_count+1,1,index)
      mins = []
      maxs = []
      names = []
      colors = []
      for subplot in sorted(data[group_key].keys()):
        x = [to_date(d) for d in data_hidden[CONFIG[subplot]['xaxis']] ]
        y = data[group_key][subplot]
        sb = ax.plot(x, y,label=subplot.split('.')[-1])
        mins.append(np.min(y))
        maxs.append(np.max(y))
        names.append(subplot.split('.')[-1])
        colors.append(sb[-1].get_color())

      ax.set_xlim(true_start,true_end)
      ax.text(1.01,1.0,"%s" %(group_key),transform=ax.transAxes, color='b', wrap=True)
      leg = ax.legend(loc="upper right",mode="expand",ncol=len(data[group_key]),bbox_to_anchor=(1., 0., 1., 1.))

      # for h, t in zip(leg.legendHandles, leg.get_texts()):
      #     t.set_color(h.get_facecolor()[0])

      ax.text(-0.25,0.00,"%.3f" % np.min(mins),transform=ax.transAxes,horizontalalignment='right')
      ax.text(-0.05,0.00,"%.3f" % np.max(maxs),transform=ax.transAxes,horizontalalignment='right')
      if index==2:
        # place headers
        ax.text(-0.25,0.7,'min',transform=ax.transAxes,horizontalalignment='right',fontweight='bold')
        ax.text(-0.05,0.7,'max',transform=ax.transAxes,horizontalalignment='right',fontweight='bold')
        # place tick labels 
        # plt.setp(ax.get_xticklabels(), rotation=80)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%y-%m-%d\n%H:%M:%S'))
        ax.tick_params(axis="x", pad=-65)
      else:
        ax.set_xticklabels([])
      ax.set_yticklabels([])
      ax.set_yticks(())
      ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=10))
      ax.xaxis.grid(True)

  fig.tight_layout(rect=[0.25, 0, 0.65, 1])
  plt.subplots_adjust(wspace=0, hspace=0.1)
 
  DPI = fig.get_dpi()
  fig.set_size_inches(2000.0/float(DPI),80*plot_count/float(DPI))

  plt.savefig("%s"%(output_filename),dpi=300)
  plt.close(fig)


def group_by_merge_and_count(data):
  groups = {}
  groups_hidden = {}
  counts = 0
  for key in data.keys():
    if not CONFIG[key]['xaxis']:
      nested_set(groups_hidden,[key],data[key])
      continue
    merge_key = CONFIG[key]['merged']
    if merge_key:
      counts += (1 if (merge_key not in groups) else 0 )
      nested_set(groups,[merge_key,key],data[key])
    else:
      counts += 1
      nested_set(groups,[key,key],data[key])
      
  return groups, groups_hidden, counts


def parse_raw(raw):
  metrics = raw['Metrics']
  ndelta = raw['NDeltas']
  plots = {}
  for index,m in enumerate(metrics):
    if m['Key'] in CONFIG:
      if CONFIG[m['Key']]["type"]=="total":
        values = fix_values(m['Value'], m['Deltas'])
      else:
        values = m['Deltas']
      plots[m['Key']] = values
  return plots




def get_parser():
  """Get parser object for script"""
  parser = ArgumentParser(description=__doc__,
            formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("-f", "--file",
            dest="input_filename",
            required=True,
            type=lambda x: is_valid_file(parser, x),
            help="decoded diagnostic file, in JSON",
            metavar="FILE")
  parser.add_argument("-o", "--output",
            required=True,
            dest="output_filename",
            help="plot filename (example.png)",
            metavar="OUT_FILE")
  parser.add_argument("-s","--scheme",
            dest="scheme",
            default="main",
            help="metric scheme: main|...")
  parser.add_argument("-d","--datemarks",
            dest="datemarks",
            default='{}',
            help="datemarks'\{\"name\":\"date\"\}'")
  # Add a --verbose and --quiet option, but don't allow both at the same time
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-v', '--verbose', action='store_true',help="verbose")
  group.add_argument('-q', '--quiet', action='store_true',help="quiet")

  return parser

def ftdc_main():
  args = get_parser().parse_args()

  if args.verbose:
        print('Opening {}#{}'.format(args.input_filename, args.extension))
  if not args.quiet:
        print('Writing {}'.format(args.output_filename))

  raw = parse_input_file(args.input_filename)
  CONFIG = parse_input_file(pkg_resources.resource_filename(__name__, "schemes/%s.json"%args.scheme))
  merged = {}
  for index, ftdc in enumerate(raw):
    data = parse_raw(ftdc)
    if index == 0: 
      merged = data
    else:
      dict_merge(merged, data)
  grouped, grouped_hidden, counted = group_by_merge_and_count(merged)
  draw_plot(grouped,grouped_hidden,counted,args.output_filename)


if __name__ == "__main__":
  ftdc_main()


