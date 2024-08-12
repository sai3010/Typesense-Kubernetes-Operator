FROM python:3.9.17
RUN pip install kopf kubernetes pyyaml
ADD handler.py deployment_utils.py /
COPY templates /templates

CMD kopf run handler.py --verbose