#!/bin/bash


export PIN="/Users/tshull7/UIUC/research/pin-2.13-65163-clang.5.0-mac/pin"
#export PINTOOL="/Users/tshull7/UIUC/research/pin-2.13-65163-clang.5.0-mac/source/tools/$pin_type/obj-intel64/${pin_type}.dylib"
export PINTOOL="/Users/tshull7/UIUC/CS598DHP/project/trace_generator/obj-intel64/GCTracer.dylib"

export PINARGS=$pin_args

CACHE_SIZE=8*1024
CACHE_LINE_SIZE=64
CACHE_ASSOCIATIVITY=16


#$PIN -t $PINTOOL -o pinlog.log -- ls .
$PIN  -t $PINTOOL -mfs -cs -c $CACHE_SIZE -l $CACHE_LINE_SIZE -a $CACHE_ASSOCIATIVITY  -o pinlog.log -- ls .
#$PIN  -t $PINTOOL -at -cs -o pinlog.log -- ls .
