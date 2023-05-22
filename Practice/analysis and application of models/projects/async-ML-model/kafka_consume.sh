#!/bin/sh

kafka-console-consumer.sh --bootstrap-server otus-bigdata.filonovpv.name:9092 \
        --topic clicks \
        --group otus