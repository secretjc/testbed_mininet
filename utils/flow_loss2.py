import csv 
import os

def get_scenario_prob(inFile):
    scenario_prob_dict = {}
    with open(inFile, 'r') as f:
        lines = [line.strip().split(' ') for line in f.readlines()[1:]]
    # print(lines)
    for line in lines:
        scenario = 'scenario_{}'.format(str(line[0]))
        scenario_prob_dict[scenario] = float(line[2])
    return scenario_prob_dict


def get_single_scenario_loss(inFile):
    loss_dict = {}
    with open(inFile, 'r') as f:
        lines = [line.strip().split(' ') for line in f.readlines()[1:]]
        # print(lines)
    for line in lines:
        src_dst_pri = (int(line[2]), int(line[3]), str(line[4]))
        loss = float(line[0])
        loss_dict[src_dst_pri] = loss
    return loss_dict


def get_flow_loss(inFileDir):
    scenario_loss_dict = {}
    scenario_prob_dict = get_scenario_prob('../_data/scenario_ibm.tab')
    for i in range(139):
        loss_file = os.path.join(inFileDir, 'ibm_{}_loss.txt'.format(str(i)))
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


def calculate_loss(h_target_pct, l_target_pct, flow_loss_dict):
    flow_loss_pct = {}
    # print(flow_loss_dict[(7,3)])
    for pair in flow_loss_dict:
        cur_pct = 0
        cur_loss = 0
        for [loss, prob] in flow_loss_dict[pair]:
            cur_loss = loss
            cur_pct += prob
            if pair[2] == "h":
                if cur_pct >= h_target_pct:
                    break
            elif pair[2] == "l":
                if cur_pct >= l_target_pct:
                    break
        flow_loss_pct[pair] = cur_loss        
    return flow_loss_pct

def loss_to_file(h_outFile, l_outFile, flow_loss_pct, h_target_pct, l_target_pct):
    fields = ['loss', 'src', 'dst', 'percentile', 'priority']
    h_rows = []
    l_rows = []
    for (src, dst, pri) in flow_loss_pct.keys():
        loss = flow_loss_pct[(src, dst, pri)]
        if pri == "h":
            h_rows.append([loss, src, dst, h_target_pct, pri])
        elif pri == "l":
            l_rows.append([loss, src, dst, l_target_pct, pri])
        
    h_rows = sorted(h_rows, reverse=True)
    l_rows = sorted(l_rows, reverse=True)
    with open(h_outFile, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(h_rows)
    with open(l_outFile, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(l_rows)


if __name__ == "__main__":
    h_target_percentile = 0.999
    l_target_percentile = 0.99
    inFileDir = "../loss_2class/"
    
    flow_loss_dict = get_flow_loss(inFileDir)
    flow_loss_pct = calculate_loss(h_target_percentile, l_target_percentile, flow_loss_dict)
    loss_to_file('../loss_2class/ibm_h.csv', '../loss_2class/ibm_l.csv', flow_loss_pct, h_target_percentile, l_target_percentile)