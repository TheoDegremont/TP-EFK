FROM fluent/fluentd:v1.16-debian

USER root

# Installer les plugins nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      ruby-dev && \
    gem install --no-document \
      'elastic-transport:8.5.1' \
      'elasticsearch-api:8.11.0' \
      'elasticsearch:8.11.0' && \
    gem install --no-document 'fluent-plugin-elasticsearch:6.0.0' && \
    gem install --no-document \
      fluent-plugin-record-modifier \
      fluent-plugin-rewrite-tag-filter \
      fluent-plugin-multi-format-parser \
      fluent-plugin-grok-parser \
      fluent-plugin-prometheus \
      fluent-plugin-detect-exceptions && \
    gem sources --clear-all && \
    apt-get purge -y --auto-remove \
      build-essential \
      ruby-dev && \
    rm -rf /var/lib/apt/lists/* \
      /home/fluent/.gem/ruby/*/cache/*.gem

USER fluent
