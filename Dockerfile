FROM alpine:3.8

MAINTAINER Lubos Mjachky <lubos.mjachky@sap.com>

RUN mkdir ODfuzz
COPY . ODfuzz/

ENV TZ=Europe/Berlin

RUN apk update \
	&& apk add --no-cache \
		build-base \
		tzdata \
	&& ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& apk add --no-cache --virtual=build-dependencies wget \
	&& apk add --no-cache \
		mongodb \
		python3 \
		libffi-dev \
		libxslt-dev \
		python3-dev \
	&& python3 -m ensurepip \
	&& pip3 install --upgrade pip \
	&& pip3 install --upgrade setuptools \
	&& pip3 install numpy \
	&& pip3 install pandas \
	&& pip3 install cffi \
	&& pip3 install -r ODfuzz/requirements.txt \
	&& apk del \
		build-base \
		build-dependencies \
		libffi-dev \
		python3-dev \
		tzdata \
	&& rm -rf ~/.pip/cache/ \
	&& rm -rf /tmp/* \
	&& rm -rf /tar/tmp/* \
	&& rm -rf /var/cache/apk/* \
	&& rm -rf /usr/lib/python*/ensurepip \
	&& rm -rf /root/.cache

ENV PROXY_ENABLED="yes" \
	HTTP_PROXY="http://proxy:8080" \
	http_proxy="http://proxy:8080" \
	HTTPS_PROXY="http://proxy:8080" \
	https_proxy="http://proxy:8080" \
	FTP_PROXY="http://proxy:8080" \
	ftp_proxy="http://proxy:8080" \
	GOPHER_PROXY="http://proxy:8080" \
	gopher_proxy="http://proxy:8080" \
	NO_PROXY="localhost, 127.0.0.1, sap-ag.de, sap.corp, corp.sap, co.sap.com, sap.biz, wdf.sap.corp, .wdf.sap.corp, .blrl.sap.corp, .phl.sap.corp, 10.68.148.36, 10.68.148.36, 10.68.148.36, .global.corp.sap, .wdf.sap.corp, .sap-ag.de, .sap.corp, .corp.sap, .co.sap.com, .sap.biz, .successfactors.com, *.sap, *.corp, *.successfactors.com, *.cloud.sap" \
	no_proxy="localhost, 127.0.0.1, sap-ag.de, sap.corp, corp.sap, co.sap.com, sap.biz, wdf.sap.corp, .wdf.sap.corp, .blrl.sap.corp, .phl.sap.corp, 10.68.148.36, 10.68.148.36, 10.68.148.36, .global.corp.sap, .wdf.sap.corp, .sap-ag.de, .sap.corp, .corp.sap, .co.sap.com, .sap.biz, .successfactors.com, *.sap, *.corp, *.successfactors.com, *.cloud.sap"

VOLUME /data/db
WORKDIR /ODfuzz

CMD mongod > /dev/null 2>&1 & sh -c sh

