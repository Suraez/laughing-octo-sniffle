FROM ghcr.io/fission/python-env:latest

# Install build tools and igraph C library
RUN apk add --no-cache \
    build-base \
    python3-dev \
    libxml2-dev \
    zlib-dev \
    glpk-dev \
    cairo-dev \
    curl \
    cmake \
    git \
    gfortran \
    && curl -L https://github.com/igraph/igraph/releases/download/0.10.8/igraph-0.10.8.tar.gz | tar xz \
    && cd igraph-0.10.8 && mkdir build && cd build \
    && cmake .. && make && make install \
    && cd / && rm -rf igraph-0.10.8 \
    && pip install --no-cache-dir python-igraph
