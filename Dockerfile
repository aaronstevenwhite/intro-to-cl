FROM quay.io/jupyter/minimal-notebook:python-3.13

RUN pip install --no-cache-dir \
    numpy \
    scipy \
    pandas \
    matplotlib \
    scikit-learn \
    nltk \
    pyparsing \
    hmmlearn \
    sklearn-crfsuite \
    rdflib \
    stanza

# pynini and arcweight require conda-forge
RUN conda install -c conda-forge pynini && conda clean -afy
