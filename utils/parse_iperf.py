import sys
import os.path

"Usage: python parse_iperf.py folder_name"

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

def topology(folder):
    max_loss1 = 0
    max_loss2 = 0
    loss_list = []
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
                max_loss1 = max(loss1, max_loss1)
                max_loss2 = max(report_loss, max_loss2)
                #print src, dst, loss1, report_loss, total_send
                #print loss1 * 100, total_send / 1000
                loss_list.append((loss1*100, loss2*100, total_send / 1000, src, dst, total_send, total_receive))
                #loss_list.append((loss2*100, total_send / 1000, src, dst))
                #loss_list.append((report_loss, total_send / 1000, src, dst, total_send, total_receive))
    #print max_loss1, max_loss2
    loss_list.sort(key=lambda x:x[1], reverse=True)
    print "loss total_send(KBytes) src dst"
    for loss1, loss2, traffic, src, dst, ts, tr in loss_list:
        #print src, dst, loss1, loss2, traffic, ts, tr
        print loss2, traffic, src, dst
    
def main(folder):
    topology(folder)

folder = sys.argv[1]
main(folder)
