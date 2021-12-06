FROM python:3.8.1-alpine
COPY setup.py README.md requirements.txt ./
COPY src ./src
COPY testcases ./testcases
RUN pip install robotframework-requests \
    && python setup.py install

ENTRYPOINT ["robot"]
CMD ["--help"]