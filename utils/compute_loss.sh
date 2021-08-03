#!/usr/bin/env bash

scenario_num=($(python read_scenario.py --scenario_file ../_data/scenario_ibm.tab| tr -d '[],'))
echo $scenario_num


for i in "${scenario_num[@]}"
do
    python2 parse_iperf.py ../ibm_scenario_${i} > ../loss/ibm_${i}_loss.txt
done