FROM python:3.11.10-slim
COPY requirements.txt /
RUN pip install -r requirements.txt --no-cache-dir && rm -Rf /root/.cache/pip
COPY handler.py deployment_utils.py /
COPY templates /templates

CMD kopf run handler.py --verbose