#!/usr/bin/env python

"""

max_concurrent_flow.py

Run with python2.7+ (but not python3)
"""
####
#### Imports
####
import sys
import time
import logging
import yaml
import argparse
from collections import defaultdict
import itertools

sys.path.append('..')
import module.tunnel.teavar as teavar

####
#### Authorship information
####
__author__ = "Yiyang Chang, Chuan Jiang"
__copyright__ = "Copyright 2016, Purdue ISL Robustness Framerwork Project"
__credits__ = ["Yiyang Chang, Chuan Jiang"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Yiyang Chang"
__email__ = "chang256@purdue.edu"
__status__ = "alpha"

def _parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--main_config", default="config/main.yaml",
                      help="main config file")
  parser.add_argument("--topo_config", default="../_config/abilene.yaml",
                      help="topology config file")
  return parser.parse_args()

def _parse_configs(args):
  with open(args.main_config, 'r') as f:
    main_config = yaml.load(f)

  with open(args.topo_config, 'r') as f:
    topo_config = yaml.load(f)

  return {'main_config': main_config, 'topo_config': topo_config}

def _compute_smore(main_config, topo_config, solver_config):
  logger = logging.getLogger('compute_ffc_tunnel')
  smore_solver = teavar.SmoreModelSolver(
      main_config=main_config,
      topo_config=topo_config,
      solver_config=solver_config)

  smore_check_solver = teavar.SmoreCheckSolver(
      main_config=main_config,
      topo_config=topo_config,
      solver_config=solver_config)

  #res, solving_time = smore_solver.compute_max_throughput()
  res, solving_time = smore_check_solver.compute_max_throughput()
  logger.info("teavar result = %s" % (res))


def _main(args, configs):
  main_config = configs['main_config']['main']
  topo_config = configs['topo_config']
  solver_config = configs['main_config']['solver']
  logging.basicConfig(level=main_config['log_level'])
  logger = logging.getLogger('main')

  logger.info("Start.")
  _compute_smore(main_config, topo_config, solver_config)
  logger.info("Done.")

if __name__ == "__main__":
  args = _parse_args()
  configs = _parse_configs(args)
  _main(args, configs)
