# Start from a core stack version
FROM jupyter/all-spark-notebook:spark-3.2.1

ARG spark_version=3.2.1
ARG hadoop_version=3.2
ARG spark_checksum=145ADACF189FECF05FBA3A69841D2804DD66546B11D14FC181AC49D89F3CB5E4FECD9B25F56F0AF767155419CD430838FB651992AEB37D3A6F91E7E009D1F9AE
ARG openjdk_version=11

USER root
RUN apt-get update -y && \
    apt-get install -y software-properties-common && \
    apt-get update -y && \
    apt-get install -y graphviz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Install from requirements.txt file
RUN pip uninstall -y h5py typing-extensions bokeh && \
    pip install typing-extensions==4.2.0 && \
    conda install -y -c anaconda h5py==3.6.0

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip config --global set http.sslVerify false \
    pip install --trusted-host pypi.org \
                --trusted-host pypi.python.org \
                --trusted-host files.pythonhosted.org \
                --default-timeout=10 \
                --quiet \
                --no-cache-dir \
                --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

ENTRYPOINT ["jupyter", "notebook", "--NotebookApp.iopub_data_rate_limit=1e10", "--ip=0.0.0.0", "--allow-root"]
