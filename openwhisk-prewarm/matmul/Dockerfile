FROM openwhisk/action-python-v3.11:latest

# Install numpy and lay down files/permissions as root
USER root
RUN pip3 install --no-cache-dir numpy
COPY prewarm.py /prewarm.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh /prewarm.py && chown 1001:0 /entrypoint.sh /prewarm.py

# Drop to the non-root user expected by the runtime
USER 1001

ENV PYTHONIOENCODING=UTF-8 \
    PREWARM_RESERVE_MIB=0     

ENTRYPOINT ["/entrypoint.sh"]