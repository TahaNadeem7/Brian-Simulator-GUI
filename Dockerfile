FROM jupyter/scipy-notebook

LABEL org.opencontainers.image.authors="ben.d.evans@gmail.com"

USER $NB_USER

RUN conda config --add channels brian-team
# RUN conda config --add channels menpo
# 'mayavi=4.5.*'

# Install Python 3 packages
RUN conda install --quiet --yes \
    'sphinx=6.1.*' \
    'brian2=2.5.*' \
    'brian2tools=0.3.*' && \
    conda clean -tipsy

ENV DISPLAY :0
