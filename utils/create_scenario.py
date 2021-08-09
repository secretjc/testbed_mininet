import yaml
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario_file', default='../_data/scenario_ibm.tab',
                        help='scenario file')
    parser.add_argument('--scenario_template', default='../_config/scenario_template.yaml',
                        help='scenario template')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    with open(args.scenario_file, 'r') as f:
        scenario_lines = [line.rstrip() for line in f][1:]
        scenario_dic = {}
        for line in scenario_lines:
            line = line.split(' ')
            scenario_dic[str(line[0])] = str(line[1])
    with open(args.scenario_template, 'r') as f:
        scenario_template = yaml.safe_load(f)
    for key in scenario_dic.keys():
        out_file = '../_config/scenario_{}.yaml'.format(key)
        # initial_file =  './_data/initialsq/initialsq_{}.tab'.format(key)
        initial_file =  './_data/initial_split/initial_{}.tab'.format(key)
        dump_scenario = scenario_template.copy()
        dump_scenario['topology']['failed_links'] = scenario_dic[key]
        dump_scenario['topology']['initial_file'] = initial_file
        with open(out_file, 'w') as f:
            yaml.safe_dump(dump_scenario, f, default_flow_style=False)


