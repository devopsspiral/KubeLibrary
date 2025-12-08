FROM python:3.9.0-alpine
COPY setup.py README.md requirements.txt ./
COPY src ./src
COPY testcases ./testcases
RUN pip install urllib3==1.26.20 robotframework-requests \
    && python setup.py install

ENTRYPOINT ["robot"]
CMD ["--help"]