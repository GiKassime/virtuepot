FROM alpine:3.12

LABEL maintainer "https://github.com/blacktop"

ARG VERSION

RUN apk add --no-cache libc6-compat curl jq

RUN \
  cd /tmp \
  && wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${VERSION}-linux-x86_64.tar.gz \
  && tar xzvf filebeat-${VERSION}-linux-x86_64.tar.gz \
  && mv filebeat-${VERSION}-linux-x86_64 /usr/share/filebeat \
  && mkdir /usr/share/filebeat/logs /usr/share/filebeat/data \
  && rm /tmp/*

ENV PATH $PATH:/usr/share/filebeat


# Copia os arquivos de configuração
COPY config /usr/share/filebeat

# Garante permissões corretas para filebeat.yml e config/filebeat.yml
RUN set -e; \
  for f in /usr/share/filebeat/filebeat.yml /usr/share/filebeat/config/filebeat.yml; do \
    if [ -f "$f" ]; then \
      chown root:root "$f" && chmod go-w "$f"; \
    fi; \
  done
RUN sudo chown root:root zeek/filebeat/config/filebeat.yml
RUN sudo chmod go-w zeek/filebeat/config/filebeat.yml

COPY entrypoint.sh /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint

WORKDIR /usr/share/filebeat

ENTRYPOINT ["entrypoint"]
CMD ["-h"]