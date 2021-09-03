import sys
import os.path

"Usage: python parse_iperf.py scenario_file folder_prefix initial_prefix"

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
            _, s, t, pri, loss = line.strip().split(' ')
            throttle[int(s), int(t), pri] = float(loss)
    fin.close()
    return throttle

def single_run(folder, initial, pri):
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
                file_name = folder + "/h%s_%s_to_h%s_%s_client.txt" % (pri, src, pri, dst)
                if not os.path.exists(file_name):
                    print file_name
                    loss_dict[(src, dst)] = 100
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
                if (src, dst, pri) in throttle:
                    print src, dst, throttle[src, dst, pri]
                    total_send2 = total_send2 / (1 - throttle[src, dst, pri])
                file_name = folder + "/h%s_%s_to_h%s_%s_server.txt" % (pri, src, pri, dst)
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
                if loss_dict[(src,dst)] > 0.5 and loss_dict[(src,dst)] < 90:
                    print src, dst, loss_dict[(src, dst)], initial
    return loss_dict

def main(scenario_file, folder_prefix, initial_prefix, pri, beta):
    prob = get_prob(scenario_file)
    loss_list_dict = {}
    for s in prob:
        print "dealing with scenario:", s
        folder = folder_prefix + str(s)
        initial = initial_prefix + str(s) + ".tab"
        loss_dict = single_run(folder, initial, pri)
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
            if count >= beta:
                res.append((loss_list[i][0], src, dst))
                break
        if count < beta:
            res.append((100, src, dst))
    res.sort(key=lambda x:x[0], reverse=True)
    for loss, src, dst in res:
        print loss, src, dst

scenario_file = sys.argv[1]
folder_prefix = sys.argv[2]
initial_prefix = sys.argv[3]
pri = sys.argv[4]
beta = float(sys.argv[5])
main(scenario_file, folder_prefix, initial_prefix, pri, beta)
