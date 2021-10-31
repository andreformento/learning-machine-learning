# Start from a core stack version
FROM jupyter/all-spark-notebook:spark-3.2.0

ARG spark_version=3.2.0
ARG hadoop_version=3.2
ARG spark_checksum=EBE51A449EBD070BE7D3570931044070E53C23076ABAD233B3C51D45A7C99326CF55805EE0D573E6EB7D6A67CFEF1963CD77D6DC07DD2FD70FD60DA9D1F79E5E
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
    pip install typing-extensions==3.7.4.3 && \
    conda install -y -c anaconda h5py==3.4.0

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip install --quiet --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

ENTRYPOINT ["jupyter", "notebook", "--NotebookApp.iopub_data_rate_limit=1e10", "--ip=0.0.0.0", "--allow-root"]
