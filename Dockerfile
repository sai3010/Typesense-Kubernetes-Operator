FROM python:3.9.19-alpine3.20
RUN pip install --upgrade pip && pip install kopf kubernetes pyyaml
ADD handler.py deployment_utils.py /
COPY templates /templates

CMD kopf run handler.py --verbose