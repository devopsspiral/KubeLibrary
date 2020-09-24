FROM python:3.8.1-alpine
COPY setup.py README.md src testcases ./
RUN ls && pip install robotframework-requests \
    && python setup.py install \
    && pwd

ENTRYPOINT robot