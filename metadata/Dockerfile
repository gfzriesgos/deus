# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

FROM python:3.7-buster

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        python3 \
        python3-pip \
        libgdal-dev \
        python3-rtree

WORKDIR /usr/share/git/deus
COPY requirements.txt .

# need to install the GDAL python version which works with the installed GDAL version
# current workaround: install GDAL via pip and reinstall again to get it working
RUN pip3 install wheel && \
    GDAL_VERSION=$(gdal-config --version) && \
    sed -i -e "s@GDAL==.*@GDAL==$GDAL_VERSION@" requirements.txt && \
    pip3 install -r requirements.txt && \
    pip3 uninstall -y GDAL && \
    pip3 install \
        GDAL==${GDAL_VERSION} \
        --global-option=build_ext \
        --global-option="-I/usr/include/gdal"

COPY . .
