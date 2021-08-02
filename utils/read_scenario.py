import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario_file', default='./_data/scenario_example.tab',
                        help='scenario file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    with open(args.scenario_file, 'r') as f:
        scenario_lines = [line.rstrip() for line in f][1:]
        scenario_list = []
        for line in scenario_lines:
            line = line.split(' ')
            scenario_list.append(int(line[0]))
        
    print(scenario_list)
