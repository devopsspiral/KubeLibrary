FROM python:3.10-alpine
COPY setup.py README.md requirements.txt pyproject.toml ./
COPY src ./src
COPY testcases ./testcases
RUN pip install robotframework-requests \
    && pip install .

ENTRYPOINT ["robot"]
CMD ["--help"]