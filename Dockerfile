FROM jupyter/minimal-notebook:x86_64-python-3.11.6

RUN conda install -c conda-forge numpy pynini stanza