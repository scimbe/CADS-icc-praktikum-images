FROM alpine:3.20

# Werkzeugkasten fuer das ICC-Praktikum: Netzwerkdiagnose ohne Zusatzrechte.
# Laeuft als Root mit den Standard-Capabilities der ICC (NET_RAW vorhanden,
# NET_ADMIN nicht), genau das, was die Praktikumsaufgaben brauchen.
RUN apk add --no-cache \
      bash curl jq \
      iproute2 iputils traceroute tcpdump \
      iperf3 bind-tools netcat-openbsd socat \
      python3 py3-scapy \
      ca-certificates

COPY lab/labsrv.py /opt/lab/labsrv.py

ENV PYTHONUNBUFFERED=1
CMD ["sleep", "infinity"]
