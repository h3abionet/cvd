FROM nfcore/base
LABEL authors="Mamana Mbiyavanga" \
      description="Docker image containing all requirements for nf-core/chipfreqs pipeline"

COPY environment.yml /
RUN conda env create -f /environment.yml && conda clean -a
ENV PATH /opt/conda/envs/nf-core-chipfreqs-1.0dev/bin:$PATH
