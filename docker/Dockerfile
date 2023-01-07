FROM continuumio/miniconda3

RUN mkdir /tmp/cdcxtoedgelist
COPY dist/*.whl /tmp/cdcxtoedgelist

RUN /opt/conda/bin/pip install /tmp/cdcxtoedgelist/cdcxtoedgelist*whl

RUN rm -rf /tmp/cdcxtoedgelist

ENTRYPOINT ["/opt/conda/bin/cdcxtoedgelistcmd.py"]
CMD ["--help"]
