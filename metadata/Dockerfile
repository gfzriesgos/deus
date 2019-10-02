FROM python:3.6.9-buster

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN apt-get update && \
    apt-get install -y python3 python3-pip libgdal-dev python3-rtree

WORKDIR /usr/share/git/deus
COPY requirements.txt .

# need to install the GDAL python version which works with the installed GDAL version
RUN pip3 install wheel && \
    pip3 install -r requirements.txt && \
    pip3 uninstall -y GDAL && \
    pip3 install GDAL==$(gdal-config --version)

COPY . .
