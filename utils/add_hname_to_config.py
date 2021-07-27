import yaml
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--main_config', default='../_config/main.yaml',
                        help='main config file')
    parser.add_argument('--server_file', default='./server.txt',
                      help='server list file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    yaml.preserve_quotes = True
    with open(args.main_config, 'r') as f:
        main_config = yaml.safe_load(f)
    with open(args.server_file, 'r') as f:
        lines = [line.rstrip() for line in f][1:]
        server_list = ["localhost"] + lines
        main_config['main']['servers'] = server_list
    with open(args.main_config, 'w') as f:
        print(main_config)
        yaml.safe_dump(main_config, f)


