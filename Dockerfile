FROM alpine:3.8

MAINTAINER Lubos Mjachky <lubos.mjachky@sap.com>

RUN mkdir ODfuzz
COPY . ODfuzz/

ENV TZ=Europe/Berlin

RUN apk upgrade \
	&& apk --update add build-base \
	&& ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& apk add --no-cache --virtual=build-dependencies wget \
	&& apk add --no-cache \
		bash \
		mongodb \
		python3 \
	&& apk add --no-cache \
		libxml2 \
		libffi-dev \
		libxslt-dev \
		libxml2-dev \
		python3-dev \
		openssl-dev \
	&& wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 \
	&& pip install cffi \
	&& pip install -r ODfuzz/requirements.txt \
	&& apk del \
		build-base \
		libxml2 \
		libffi-dev \
		libxml2-dev \
		python3-dev \
		openssl-dev \
	&& rm -rf ~/.pip/cache/ \
	&& rm -rf /var/cache/apk/*

VOLUME /data/db

