FROM alpine:3.8

LABEL key="Petr Hanak  <petr.hanak@sap.com>"

ENV TZ=Europe/Berlin

# install system dependencies 
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
	&& pip3 install cffi

# since dependencies change less often than rest of code, install them in separate layer
COPY ./requirements.txt /tmp/ 
RUN pip install -r /tmp/requirements.txt

# everything around odfuzz to be runnable in container
RUN mkdir /odfuzz
COPY . /odfuzz/
WORKDIR /odfuzz
RUN python3 setup.py install

ENTRYPOINT [ "odfuzz" ]