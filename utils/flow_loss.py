import csv 


def get_flow_loss(target_percentile, inFileDir):
    scenario_loss_dict = {}
    scenario_prob_dict = get_scenario_prob('../_data/scenario_ibm.tab')
    for i in range(139):
        loss_file = '../loss/ibm_{}_loss.txt'.format(str(i))
        scenario = 'scenario_{}'.format(str(i))
        scenario_loss_dict[scenario] = get_single_scenario_loss(loss_file)
    flow_loss_dict = {}
    for i in range(139):
        scenario = 'scenario_{}'.format(str(i))
        current_percentile = scenario_prob_dict[scenario]
        current_scenario_loss = scenario_loss_dict[scenario]
        for pair in current_scenario_loss.keys():
            loss = current_scenario_loss[pair]
            if pair not in flow_loss_dict.keys():
                flow_loss_dict[pair] = []
            flow_loss_dict[pair].append([loss, current_percentile])
    for pair in flow_loss_dict.keys():
        flow_loss_dict[pair] = sorted(flow_loss_dict[pair])
    return flow_loss_dict

def get_single_scenario_loss(inFile):
    loss_dict = {}
    with open(inFile, 'r') as f:
        lines = [line.strip().split(' ') for line in f.readlines()[1:]]
        # print(lines)
    for line in lines:
        src_dst = (int(line[2]), int(line[3]))
        loss = float(line[0])
        loss_dict[src_dst] = loss
    return loss_dict

def get_scenario_prob(inFile):
    scenario_prob_dict = {}
    with open(inFile, 'r') as f:
        lines = [line.strip().split(' ') for line in f.readlines()[1:]]
    # print(lines)
    for line in lines:
        scenario = 'scenario_{}'.format(str(line[0]))
        scenario_prob_dict[scenario] = float(line[2])
    return scenario_prob_dict

def calculate_loss(target_pct, flow_loss_dict):
    flow_loss_pct = {}
    # print(flow_loss_dict[(7,3)])
    for pair in flow_loss_dict:
        cur_pct = 0
        cur_loss = 0
        for [loss, prob] in flow_loss_dict[pair]:
            cur_loss = loss
            cur_pct += prob
            if cur_pct >= target_pct:
                break
        flow_loss_pct[pair] = cur_loss        
    return flow_loss_pct

def loss_to_file(outFile, flow_loss_pct, target_pct):
    fields = ['loss', 'src', 'dst', 'percentile']
    rows = []
    for (src, dst) in flow_loss_pct.keys():
        loss = flow_loss_pct[(src, dst)]
        rows.append([loss, src, dst, target_pct])
    rows = sorted(rows, reverse=True)
    with open(outFile, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)


if __name__ == "__main__":
    target_percentile = 0.999
    inFileDir = "../loss/"

    flow_loss_dict = get_flow_loss(target_percentile, inFileDir)
    flow_loss_pct = calculate_loss(target_percentile, flow_loss_dict)
    loss_to_file('../loss/ibm.csv', flow_loss_pct, target_percentile)