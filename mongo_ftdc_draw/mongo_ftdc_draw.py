# -*- coding: utf-8 -*-

"""FTDC drawer"""

import pkg_resources
from functools import partial
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os, numpy as np
import matplotlib.pyplot as plt
import matplotlib
from .utils import *
import json

plt.rc('font', size=7)  
plt.rc('lines', linewidth=0.8)
plt.rc('lines', color='r')
plt.rc('legend', labelspacing=1)
plt.rc('axes.formatter',useoffset=False)
plt.rcParams['axes.formatter.useoffset'] = False



# from mpld3 import plugins, utils


VERBOSE = False
QUIET = False


def draw_plot(data, data_hidden, plot_count, output_filename, interactive, datemarks, scheme):
  figsize = len(scheme)*2
  fig = plt.figure(figsize=(10, 2))
  renderer = fig.canvas.get_renderer()

  if VERBOSE:
    print('Group_keys {}'.format(','.join(sorted(data.keys()))))

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

      make_fill = True if len(data[group_key].keys()) == 1 else False
      for subplot in sorted(data[group_key].keys()):
        y = data[group_key][subplot] + [data[group_key][subplot][-1]]*(len(data_hidden[scheme[subplot]['xaxis']])-len(data[group_key][subplot]))
        x = [to_date(d) for d in data_hidden[scheme[subplot]['xaxis']]] + [to_date(data_hidden[scheme[subplot]['xaxis']][-1])]*(len(data_hidden[scheme[subplot]['xaxis']])-len(y))
        name = get_plot_label(subplot,scheme)
        mins.append(np.min(y))
        maxs.append(np.max(y))
        names.append(name)
        if make_fill:
          sb = ax.fill_between(x, y,label=name, facecolor=(0,0,0,0.05), edgecolor=(0,0,0,1),linewidth=0.8) 
          colors.append(sb.get_facecolor()[0][:3])
        else:
          sb = ax.plot(x, y,label=name)
          colors.append(sb[-1].get_color())
        
        

      
      ax.text(1.01,0.8,"%s" %(group_key),transform=ax.transAxes, color='b', wrap=True)
      # leg = ax.legend(loc="upper right",mode="expand",ncol=len(data[group_key]),bbox_to_anchor=(1., 0., 1., 1.))

      tt = ax.transAxes
      for txt,c in zip(names,colors):
        legend_t = plt.text(1.01,0.5,txt,transform=tt, color=c, wrap=True)
        ex = legend_t.get_window_extent(renderer=renderer)
        tt = matplotlib.transforms.offset_copy(legend_t._transform, x=ex.width*3.1, units='dots')
      
        
      y_min = np.min(mins)
      y_max = np.max(maxs)
      ax.set_xlim(true_start,true_end)
      ax.set_ylim(y_min-y_min*0.1-0.00001,y_max*1.1+0.00001, auto=True)
      ax.text(-0.20,0.00,"%.3f" % y_min,transform=ax.transAxes,horizontalalignment='right')
      ax.text(-0.10,0.00,"%.3f" % y_max,transform=ax.transAxes,horizontalalignment='right')

      for datemark, date in datemarks.items():
          ax.axvline(x=string_to_date(date),ymin=-0.2, ymax=1.1,clip_on=False,linewidth=0.5)

      if index==2:
        for datemark, date in datemarks.items():
          ax.text(string_to_date(date),ax.get_ylim()[1]*1.10,datemark,color='r')

        # place headers
        ax.text(-0.20,0.7,'min',transform=ax.transAxes,horizontalalignment='right',fontweight='bold')
        ax.text(-0.10,0.7,'max',transform=ax.transAxes,horizontalalignment='right',fontweight='bold')
        # place tick labels 
        # plt.setp(ax.get_xticklabels(), rotation=80)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%y-%m-%d\n%H:%M:%S'))
        ax.tick_params(axis="x", pad=-75)
      else:
        ax.set_xticklabels([])
      # ax.set_yticklabels([])
      # ax.set_yticks(())   
      ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator(minticks=10)) 
      ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3,min_n_ticks=3)) 
      ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.00f'))
      ax.grid(True,linestyle=':', linewidth=0.8)

  fig.tight_layout(rect=[0.10, 0, 0.75, 0.8])
  plt.subplots_adjust(wspace=0, hspace=0.1 )
 
  DPI = fig.get_dpi()
  fig.set_size_inches(2000.0/float(DPI),80*plot_count/float(DPI))

  
  if interactive:
    plt.show()
  else:
    plt.savefig("%s"%(output_filename),dpi=300)
  plt.close(fig)


def group_by_merge_and_count(data,scheme):
  groups = {}
  groups_hidden = {}
  counts = 0
  for key in data.keys():
    if not scheme[key]['xaxis']:
      nested_set(groups_hidden,[key],data[key])
      continue
    merge_key = scheme[key]['merged']
    if merge_key:
      counts += (1 if (merge_key not in groups) else 0 )
      nested_set(groups,[merge_key,key],data[key])
    else:
      counts += 1
      nested_set(groups,[key,key],data[key])
      
  return groups, groups_hidden, counts


def parse_raw(raw,scheme):
  metrics = raw['Metrics']
  ndelta = raw['NDeltas']
  plots = {}
  for index,m in enumerate(metrics):
    if m['Key'] in scheme:
      if scheme[m['Key']]["type"]=="total":
        values = fix_values(m['Value'], m['Deltas'])
      else:
        values = m['Deltas']
      if "metric" in scheme[m['Key']]:
        if (scheme[m['Key']]['metric'] == "MB") or (scheme[m['Key']]['metric'] == "MB/s"):
          values = [ bytes_to_mb(v) for v in values ]
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
  parser.add_argument("-s","--scheme",
            dest="scheme",
            default="main",
            help="metric scheme: main|...")
  parser.add_argument("-d","--datemarks",
            dest="datemarks",
            default='{}',
            help="datemarks'\{\"name\":\"date\"\}'")
  # Add a --verbose and --quiet option, but don't allow both at the same time
  group1 = parser.add_mutually_exclusive_group()
  group1.add_argument('-v', '--verbose', action='store_true',help="verbose")
  group1.add_argument('-q', '--quiet', action='store_true',help="quiet")

  group2 = parser.add_mutually_exclusive_group()
  group2.add_argument("-o", "--output",
            dest="output_filename",
            help="plot filename (example.png)",
            metavar="OUT_FILE")
  group2.add_argument('-i', '--interactive', action='store_true',help="interactive mode")

  return parser

def ftdc_main():
  args = get_parser().parse_args()
  VERBOSE = args.verbose
  QUIET = args.quiet

  if VERBOSE:
        print('Opening {}#{}'.format(args.input_filename, args.extension))
  if not QUIET:
        print('Writing {}'.format(args.output_filename))

  scheme = parse_input_file(pkg_resources.resource_filename(__name__, "schemes/%s.json"%args.scheme))
  raw = parse_input_file(args.input_filename)
  datemarks = json.loads(args.datemarks)
  
  merged = {}
  for index, ftdc in enumerate(raw):
    data = parse_raw(ftdc,scheme)
    # print(merged.keys(), data.keys())
    if index == 0: 
      merged = data
    else:
      dict_merge(merged, data)

  grouped, grouped_hidden, counted = group_by_merge_and_count(merged,scheme)
  draw_plot(grouped,grouped_hidden,counted,args.output_filename,args.interactive,datemarks,scheme)


if __name__ == "__main__":
  ftdc_main()


