#!/usr/bin/env bash
set -e
spark-submit --master local[2] /opt/app/streaming/spark_streaming_dq.py
