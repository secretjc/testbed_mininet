import sys
import os.path
import csv

"Usage: python parse_throttle_iperf.py scenario_file folder_prefix initial_prefix"

num_node = 17
eps = 0.000001
st = -1
en = 32
neglect = []# [(6,1), (2,15), (6,11), (7,8)] #[(11, 8)]

def scale(line):
    if "KByte" in line:
        return 1000
    if "MByte" in line:
        return 1000 * 1000
    return 1

def get_prob(scenario_file):
    prob = {}
    fin = open(scenario_file)
    for line in fin.readlines():
        if "s" in line:
            continue
        num, e_list, p = line.strip().split(' ')
        prob[int(num)] = float(p)
    return prob

def get_initial(initial):
    throttle = {}
    fin = open(initial)
    for line in fin.readlines():
        if "throttle" in line:
            _, s, t, loss = line.strip().split(' ')
            throttle[int(s), int(t)] = float(loss)
    fin.close()
    return throttle

def single_run(folder, initial):
    throttle = get_initial(initial)
    max_loss1 = 0
    max_loss2 = 0
    loss_dict = {}
    for src in range(num_node):
        for dst in range(num_node):
            if src != dst and (src, dst) not in neglect:
                report_loss = None
                total_send = 0
                total_receive = 0
                total_send2 = 0
                total_receive2 = 0
                file_name = folder + "/h_%s_to_h_%s_client.txt" % (src, dst)
                if not os.path.exists(file_name):
                    loss_list.append((100, 100, "None-Exist", src, dst, 0, 0))
                    continue
                fin = open(file_name)
                for line in fin.readlines():
                    if 'bits/sec' in line:
                        t1 = float(line.split('-')[0].split()[-1])
                        t2 = float(line.split('-')[1].split()[0])
                        if t1 < st:
                            t1 = st
                        if t2 > en:
                            t2 = en
                        if t2 - t1 > eps and t2 - t1 < 5:
                            total_send += float(line.split('-')[1].split()[2]) * scale(line)
                        if t2 - t1 > eps and t2 - t1 >= 5:
                            total_send2 = float(line.split('-')[1].split()[2]) * scale(line)
                            #print "   ", float(line.split('-')[1].split()[2])
                fin.close()
                if (src, dst) in throttle:
                    #print src, dst, throttle[src, dst]
                    total_send2 = total_send2 / (1 - throttle[src, dst])
                file_name = folder + "/h_%s_to_h_%s_server.txt" % (src, dst)
                fin = open(file_name)
                for line in fin.readlines():
                    if 'bits/sec' in line:
                        t1 = float(line.split('-')[0].split()[-1])
                        t2 = float(line.split('-')[1].split()[0])
                        if t1 < st:
                            t1 = st
                        if t2 > en:
                            t2 = en
                        if t2 - t1 > eps and t2 - t1 < 5:
                            total_receive += float(line.split('-')[1].split()[2]) * scale(line)
                        if t2 - t1 > eps and t2 - t1 >= 5:
                            #print line
                            total_receive2 = float(line.split('-')[1].split()[2]) * scale(line)
                            report_loss = float(line.split('-')[1].split()[-1][1:-2])
                fin.close()
                if total_send > total_receive:   #loss1 -> cumulated
                    loss1 = (total_send - total_receive) / total_send
                else:
                    loss1 = 0
                if total_send2 > total_receive2:    #loss2 -> summary
                    loss2 = (total_send2 - total_receive2) / total_send2
                else:
                    loss2 = (total_send2 - total_receive2) / total_send2 #0
                loss_dict[(src,dst)] = loss2*100
    return loss_dict

def main(scenario_file, folder_prefix, initial_prefix, outfilename):
    prob = get_prob(scenario_file)
    loss_list_dict = {}
    for s in prob:
        print "dealing with scenario:", s
        folder = folder_prefix + str(s)
        initial = initial_prefix + str(s) + ".tab"
        loss_dict = single_run(folder, initial)
        for src, dst in loss_dict:
            if (src, dst) not in loss_list_dict:
                loss_list_dict[(src, dst)] = []
            loss_list_dict[(src, dst)].append((loss_dict[src,dst], prob[s]))
    res = []
    for src, dst in loss_list_dict:
        loss_list = loss_list_dict[src,dst]
        loss_list.sort(key=lambda x:x[0])
        count = 0
        for i in range(len(loss_list)):
            count += loss_list[i][1]
            if count >= 0.999:
                res.append((loss_list[i][0], src, dst))
                break
        if count < 0.999:
            res.append((100, src, dst))
    res.sort(key=lambda x:x[0], reverse=True)
    with open(outfilename, 'w') as csvfile: 
        fields = ['loss', 'src', 'dst', 'percentile']
        rows = []
        for loss, src, dst in res:
            rows.append([loss, src, dst])
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)
        # for loss, src, dst in res:
        #     print loss, src, dst

scenario_file = sys.argv[1]
folder_prefix = sys.argv[2]
initial_prefix = sys.argv[3]
outfilename = sys.argv[4]
main(scenario_file, folder_prefix, initial_prefix, outfilename)

# python2 parse_throttle_iperf.py ../_data/scenario_ibm.tab ../iperf_results/ibm_raw/sq_15/ibm_scenario_ ../_data/initialsq/initialsq_ ../iperf_results/ibm_loss/ibm_sq_15.csv