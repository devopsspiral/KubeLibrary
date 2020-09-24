FROM python:3.8.1-alpine
COPY setup.py src/ testcases/ ./
RUN pip install robotframework-requests \
    && python setup.py install \
    && pwd

ENTRYPOINT robot