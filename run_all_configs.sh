#!/bin/bash

SCRIPT_LOC=run_dacapo_v1.sh
#OTHER_ARGS="--serial_gc --detailed_gc"
#OTHER_ARGS="--pin --serial_gc --detailed_gc"
GC_BASE="dacapo_v1_gc"
PIN_BASE="dacapo_v1_pin"
PAPI_BASE="dacapo_v1_papi"
#SAMPLE_RATE=50
SAMPLE_RATE=10
USE_PIN="no"
LOG_GC="no"
USE_PAPI="no"
PAPI_NAME="empty"

declare -a v1_size_options=(
#'large_data'
#'END'
'max_size'
'END'
'small_data'
'large_data'
'default_data'
'END'
)

declare -a v2_size_options=(
#'large_data'
#'END'
'max_size'
'END'
'small_data'
'large_data'
'default_data'
'huge_data'
'END'
)

declare -a gc_options=(
'serial_serial_gc'
'parallel_both_gc'
'parallel_serial_gc'
'END'
'conc_mark_sweep_gc'
'g1_gc'
'END'
)

declare -a pintool_choices=(
#"/home/tshull226/Documents/school/DHP_CS598/trace_generator/obj-intel64/GCTracer.so"
"/home/tshull226/Documents/school/DHP_CS598/parallel_trace_generator/obj-intel64/GCTracer.so"
"/home/tshull226/Documents/school/DHP_CS598/parallel_trace_generator/obj-intel64/GCTracer.so"
"/home/tshull226/Documents/school/DHP_CS598/parallel_trace_generator/obj-intel64/GCTracer.so"
"/home/tshull226/Documents/school/DHP_CS598/parallel_trace_generator/obj-intel64/GCTracer.so"
'END'
)

size_options=("${v1_size_options[@]}")

run_configs(){
    local count=0

    if [[ "$LOG_GC" == "yes" ]]; then
        rm -rf $GC_BASE
        mkdir $GC_BASE
    fi
    if [[ "$USE_PIN" == "yes" ]]; then
        rm -rf $PIN_BASE
        mkdir $PIN_BASE
    fi
    if [[ "$USE_PAPI" == "yes" ]]; then
        rm -rf $PAPI_BASE
        mkdir $PAPI_BASE
    fi

    while [[ ${size_options[count]} != 'END' ]]
    do
        size=${size_options[count]}
        gc_dir=$GC_BASE/$size
        if [[ "$LOG_GC" == "yes" ]]; then
            mkdir $gc_dir
        fi
        pin_dir=$PIN_BASE/$size
        if [[ "$USE_PIN" == "yes" ]]; then
            mkdir $pin_dir
        fi
        papi_dir=$PAPI_BASE/$size
        if [[ "$USE_PAPI" == "yes" ]]; then
            mkdir $papi_dir
        fi
        local gcCount=0
        while [[ ${gc_options[gcCount]} != 'END' ]]
        do
            OTHER_ARGS=""
            rm -rf scratch #removing the scratch dir
            gc_type=${gc_options[gcCount]}
            pintool=${pintool_choices[gcCount]}
            if [[ "$LOG_GC" == "yes" ]]; then
                gc_dir=$GC_BASE/$size/$gc_type
                mkdir $gc_dir
                OTHER_ARGS="$OTHER_ARGS --detailed_gc --gc_log $gc_dir"
            fi
            if [[ "$USE_PIN" == "yes" ]]; then
                pin_dir=$PIN_BASE/$size/$gc_type
                mkdir $pin_dir
                OTHER_ARGS="$OTHER_ARGS --pin --send_markers_to_pin --pin_log $pin_dir --pintool $pintool"
            fi
            if [[ "$USE_PAPI" == "yes" ]]; then
                papi_dir=$PAPI_BASE/$size/$gc_type
                mkdir $papi_dir
                OTHER_ARGS="$OTHER_ARGS --papi_monitor --papi_sampling --papi_sampling_rate $SAMPLE_RATE --papi_result $papi_dir"
                if [[ "$PAPI_NAME" != "empty" ]]; then
                OTHER_ARGS="$OTHER_ARGS --papi_config configs/${PAPI_NAME}.txt"
                fi
            fi

            ./${SCRIPT_LOC} $OTHER_ARGS --${gc_type} --${size}
            gcCount=$(( $gcCount + 1 ))
        done
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
            GC_BASE="dacapo_v2_gc"
            PIN_BASE="dacapo_v2_pin"
            PAPI_BASE="dacapo_v2_papi"
            ;;
        -p|--use_pin)
            USE_PIN="yes"
            ;;
        -gc|--gc_log)
            LOG_GC="yes"
            ;;
        -pc|--papi)
            USE_PAPI="yes"
            ;;
        -pn|--papi_name)
            PAPI_NAME=$2
            PAPI_BASE="${PAPI_BASE}_${PAPI_NAME}"
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
