#!/bin/bash

SCRIPT_LOC=run_dacapo_v1.sh
OTHER_ARGS="--serial_gc --detailed_gc"
OTHER_ARGS="--pin --serial_gc --detailed_gc"
GC_BASE="dacapo_v1"
PIN_BASE="dacapo_v1_pin"

declare -a v1_size_options=(
'small_data'
'large_data'
'default_data'
'END'
)

declare -a v2_size_options=(
'small_data'
'large_data'
'default_data'
'huge_data'
'END'
)

size_options=("${v1_size_options[@]}")

run_configs(){
    local count=0
    rm -rf $GC_BASE
    mkdir $GC_BASE
    rm -rf $PIN_BASE
    mkdir $PIN_BASE
    while [[ ${size_options[count]} != 'END' ]]
    do
        rm -rf scratch #removing the scratch dir
        size=${size_options[count]}
        gc_dir=$GC_BASE/$size
        mkdir $gc_dir
        pin_dir=$PIN_BASE/$size
        mkdir $pin_dir
        ./${SCRIPT_LOC} $OTHER_ARGS --${size} --gc_log $gc_dir --pin_log $pin_dir
        count=$(( $count + 1 ))
    done

}


while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        -v2|--use_v2)
            SCRIPT_LOC=run_dacapo_v2.sh
            size_options=("${v2_size_options[@]}")
            GC_BASE="dacapo_v2"
            PIN_BASE="dacapo_v2_pin"
            shift
            ;;
        *)
            echo "unknown option"
            exit -1
            ;;
    esac
    
    #moving onto next argument
    shift
done

run_configs
