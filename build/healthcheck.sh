#!/usr/bin/env bash
curl -f 0.0.0.0:9600/_node/stats/pipeline?pretty || exit 1