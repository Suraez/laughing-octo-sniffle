FROM openwhisk/python3action:latest

RUN pip install --upgrade pip
RUN pip install torch==2.2.1


COPY simple_model.pth /action/simple_model.pth
COPY __main__.py /action/__main__.py

CMD ["/bin/bash", "-c", "cd /actionProxy && python -u actionproxy.py"]
