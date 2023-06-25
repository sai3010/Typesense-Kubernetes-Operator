FROM python:3.8.16-slim

RUN pip install kopf kubernetes pyyaml
ADD handler.py deployment_utils.py /
COPY templates /templates

CMD kopf run handler.py --verbose