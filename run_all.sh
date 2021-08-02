#!/usr/bin/env bash

scenario_num=($(python ./utils/read_scenario.py | tr -d '[],'))
echo $scenario_num
for i in "${scenario_num[@]}"
do
   python main.py --main_config ./_config/main.yaml --topo_config ./_config/scenario_${i}.yaml
done