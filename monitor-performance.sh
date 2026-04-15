#!/bin/bash

echo "=== Monitoring EFK Performance ==="

while true; do
  echo "$(date '+%Y-%m-%d %H:%M:%S')"

  # Documents dans Elasticsearch
  echo -n "Documents in ES: "
  curl -s "localhost:9200/fluentd-*/_count" | jq '.count'

  # Taux d'indexation
  echo -n "Indexing rate: "
  curl -s "localhost:9200/_nodes/stats/indices" | jq '.nodes[].indices.indexing.index_current'

  # Utilisation mémoire Elasticsearch
  echo -n "ES Memory: "
  docker stats elasticsearch --no-stream --format "{{.MemUsage}}"

  # Buffer Fluentd
  echo -n "Fluentd buffer: "
  docker exec fluentd ls -lh /fluentd/buffer 2>/dev/null | wc -l

  echo "---"
  sleep 5
done
