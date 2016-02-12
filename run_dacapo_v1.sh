#!/bin/bash

declare -a benchmarks=(
'antlr'
#'batik' #this one throws an error
'bloat'
'chart'
'eclipse'
'fop'
'hsqldb'
'jython'
'luindex'
'lusearch'
'pmd'
#'sunflow' # this one throws an error
'xalan'
'END'
)

benchmarks=(
'xalan'
'END'
)


BENCH_DIR=~/Dropbox/CS_598DHP/benchmarks/dacapo-2006-10-MR2.jar
BENCHMARK_ARGS=""
JAVA_ARGS=""
LOG_DIR="empty"
JAVA_PATH=""

#java -jar $BENCH_DIR -h
#exit 0

unamestr=`uname`
platform='unknown'


if [[ "$unamestr" == 'Linux' ]]; then
    platform='linux'
elif [[ "$unamestr" == 'Darwin' ]]; then
    platform='mac'
fi

case $platform in
    'linux')
        #JAVA_PATH="java"
        #JAVA_PATH="/home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-release/jdk/bin/java"
        #JAVA_PATH="/home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-fastdebug/jdk/bin/java"
        JAVA_PATH="/home/tshull226/Documents/school/CS598DHP/project/debug/slowdebug/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
        # export PATH="/home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-release/jdk/bin:$PATH"
        ;;
    'mac')
        JAVA_PATH="java"
        ;;
esac

run_on_benchmarks(){
    local count=0
    while [[ ${benchmarks[count]} != 'END' ]]
    do
        benchmark=${benchmarks[count]}
        echo "benchmark: $benchmark"
        if [[ "$LOG_DIR" != "empty" ]]; then
            JAVA_ARGS="${JAVA_ARGS} -Xloggc:${LOG_DIR}/$benchmark-gc.log"
        fi
        #java -jar $BENCH_DIR -i $benchmark
        $JAVA_PATH -version
        $JAVA_PATH $JAVA_ARGS -jar $BENCH_DIR $BENCHMARK_ARGS $benchmark
        count=$(( $count + 1 ))
    done

}

#this is what actually runs
while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        --debug)
            #JAVA_PATH="gdb --args /home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-fastdebug/jdk/bin/java"
            #CURRENTLY NOT WORKING
            JAVA_PATH="/home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-fastdebug/jdk/bin/java"
            JAVA_PATH="gdb --args /home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-release/jdk/bin/java"
            JAVA_PATH="gdb --args /home/tshull226/Documents/school/CS598DHP/project/jdk8u60/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
            JAVA_PATH="gdb --args /home/tshull226/Documents/school/CS598DHP/project/debug/slowdebug/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
            ;;
        --mark_gc_phases)
            JAVA_ARGS="$JAVA_ARGS -XX:+MarkGCStartEnd"
            ;;
        --small_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s small"
            ;;
        --large_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s large"
            ;;
        --default_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s default"
            ;;
        --gc_log)
            LOG_DIR=$2
            shift
            ;;
        --detailed_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+PrintGCDetails -XX:+PrintGCDateStamps"
            ;;
        --serial_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseSerialGC"
            ;;
        --show_info)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -i"
            ;;
        *)
            echo "unknown option"
            exit -1
            ;;
    esac
    #moving onto next argument
    shift
done

run_on_benchmarks
