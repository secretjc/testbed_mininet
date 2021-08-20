import csv
import statistics
from collections import defaultdict

def get_median_loss_dict():
    loss_dict = defaultdict(list)
    for i in range(1,6):
        filename = "../iperf_results/ibm_loss/ibm_sq_1{}.csv".format(i)
        with open(filename, "r") as f:
            lines = [ e.strip().split(",") for e in f.readlines()[1:] ]
        for loss,src,dst in lines:
            loss_dict[(src,dst)].append(loss)
    for key in loss_dict.keys():
        loss_dict[key].sort()
    return loss_dict


def loss_to_file(outFile, loss_dict, target_pct):
    fields = ['loss', 'src', 'dst', 'percentile']
    rows = []
    for (src, dst) in loss_dict.keys():
        loss = statistics.median(loss_dict[(src, dst)])
        rows.append([loss, src, dst, target_pct])
    rows = sorted(rows, reverse=True)
    with open(outFile, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields) 
        csvwriter.writerows(rows)

if __name__ == "__main__":
    loss_dict = get_median_loss_dict()
    target_pct = 0.999
    outFile = "../iperf_results/ibm_loss/ibm_sq_median_11-15.csv"
    loss_to_file(outFile, loss_dict, target_pct)
