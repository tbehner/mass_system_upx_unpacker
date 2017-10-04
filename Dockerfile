FROM alpine
RUN apk add --no-cache python3 && \
    apk add --no-cache git
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
ADD . /
ENTRYPOINT python3 upx_unpacker_analysis_instance.py
