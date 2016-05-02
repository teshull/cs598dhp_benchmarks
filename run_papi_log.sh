#!/bin/bash

#for v1
./run_all_configs.sh --papi --papi_name DL1
./run_all_configs.sh --papi --papi_name IL1
./run_all_configs.sh --papi --papi_name L2
./run_all_configs.sh --papi --papi_name LLC
#
##for v2
./run_all_configs.sh --use_v2 --papi --papi_name DL1
./run_all_configs.sh --use_v2 --papi --papi_name IL1
./run_all_configs.sh --use_v2 --papi --papi_name L2
./run_all_configs.sh --use_v2 --papi --papi_name LLC
