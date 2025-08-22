FROM openwhisk/action-python-v3.11:latest

# Do file installs/permissions as root
USER root
COPY prewarm.py /prewarm.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh /prewarm.py && chown 1001:0 /entrypoint.sh /prewarm.py

# Run as the non-root user expected by the base image
USER 1001

ENV PYTHONIOENCODING=UTF-8 \
    PREWARM_RESERVE_MIB=4096

# Our entrypoint will pre-allocate memory, then chain to the OpenWhisk proxy
ENTRYPOINT ["/entrypoint.sh"]
