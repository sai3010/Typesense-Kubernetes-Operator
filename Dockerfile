FROM python:3.9.18-alpine3.19
RUN pip install --upgrade pip && pip install kopf kubernetes pyyaml
ADD handler.py deployment_utils.py /
COPY templates /templates

CMD kopf run handler.py --verbose