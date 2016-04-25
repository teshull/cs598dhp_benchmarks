#!/bin/bash

#./run_dacapo_v1.sh --serial_gc --detailed_gc --large_data
#./run_dacapo_v1.sh --mark_gc_phases --serial_gc --detailed_gc --large_data
#note that the default is parallel scavenge
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --serial_serial_gc
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --parallel_both_gc
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --parallel_serial_gc
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --conc_mark_sweep_gc
#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --g1_gc


#./run_dacapo_v1.sh --mark_gc_phases --detailed_gc --large_data --conc_mark_sweep_gc

#./run_dacapo_v1.sh --debug --serial_serial_gc --papi_monitor
#./run_dacapo_v1.sh --serial_serial_gc --papi_monitor
#./run_dacapo_v1.sh --ded --conc_mark_sweep_gc

#./run_dacapo_v1.sh --papi_monitor
#./run_dacapo_v1.sh --debug
#./run_dacapo_v1.sh --send_markers_to_pin
./run_dacapo_v1.sh --papi_monitor --papi_sampling --papi_result /home/tshull226/Documents/school/DHP_CS598/benchmarks/papi_result.txt

