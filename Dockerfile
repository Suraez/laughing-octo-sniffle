FROM fission/python-env-3.9

# Install system packages needed by igraph
RUN apk add --no-cache \
    build-base \
    python3-dev \
    libxml2-dev \
    libzip-dev \
    glpk-dev \
    pkgconfig \
    cairo-dev \
    gfortran \
    openblas-dev \
    lapack-dev

# Install Python packages
RUN pip install --no-cache-dir numpy python-igraph
