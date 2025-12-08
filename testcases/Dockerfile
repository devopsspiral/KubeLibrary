FROM python:3.9.0-alpine
COPY setup.py README.md requirements.txt ./
COPY src ./src
COPY testcases ./testcases
RUN pip install robotframework-requests \
    && python setup.py install
RUN unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

ENTRYPOINT ["robot"]
CMD ["--help"]