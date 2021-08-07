"""
Main function.
Run with Python2.7+
"""

import sys
import logging
import argparse

import yaml

import testbed


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--main_config', default='./_config/main.yaml',
                      help='main config file')
  parser.add_argument('--topo_config',
                      default='./_config/topo.yaml',
                      help='topology config file')
  return parser.parse_args()

def parse_configs(args):
  with open(args.main_config, 'r') as f:
    main_config = yaml.load(f)

  with open(args.topo_config, 'r') as f:
    topo_config = yaml.load(f)

  return {'main_config': main_config, 'topo_config': topo_config}


if __name__ == '__main__':
    # Set Mininet log level
    testbed.setLogLevel('info')

    # Parse command line arguments
    args = parse_args()

    # Load configuration
    configs = parse_configs(args)

    # Set testbed log level
    log_level = configs['main_config']['main']['log_level']
    log_file = configs['main_config']['main']['log_file']
    is_cluster = configs['main_config']['main']['is_cluster']
    logging.basicConfig(
        level=log_level, filename=log_file, filemode='w',
        format="[%(asctime)s] [%(levelname)7s] %(message)s (%(filename)s:%(lineno)s)")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)7s] %(message)s (%(filename)s:%(lineno)s)"))
    logging.getLogger('').addHandler(console)

    # Start testbed
    testbed.Testbed(configs, is_cluster).start()
