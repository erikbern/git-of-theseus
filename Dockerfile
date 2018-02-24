FROM python:2.7.12
MAINTAINER Jim DeLois <delois@adobe.com>

COPY ./container/ /
COPY ./ /got/

RUN pip install -e /got && \
    apt-get update -q && \
    apt-get install -yqq git

#VOLUME ["/output"]

WORKDIR /got/

CMD ["python"]
