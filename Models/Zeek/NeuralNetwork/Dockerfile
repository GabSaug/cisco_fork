FROM ubuntu:bionic

RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y python3.7 python3.7-dev python3-pip pkgconf python3-h5py \
    gfortran libblas3 liblapack3 liblapack-dev libblas-dev python3-setuptools && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2

RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

RUN pip3 install Cython==0.29.30 && \
    pip3 install numpy==1.21.6 && \
    pip3 install pybind11==2.9.2 && \
    pip3 install pythran==0.11.0 && \
    pip3 install SciPy==1.7.3

RUN mkdir /code
COPY requirements.txt /code/
RUN pip3 install -r /code/requirements.txt
RUN pip install protobuf==3.20.*

COPY zeek_nn.py /code/
COPY core/ /code/core/
COPY model_checkpoint/ /code/model_checkpoint/
COPY model_checkpoint_2024-06-14/ /code/model_checkpoint_2024-06-14/
