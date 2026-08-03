FROM python:3.14-slim
COPY setup.py README.md requirements.txt pyproject.toml ./
COPY src ./src
COPY testcases ./testcases
RUN pip install robotframework-requests \
    && pip install .

ENTRYPOINT ["robot"]
CMD ["--help"]