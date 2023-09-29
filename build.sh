#!/usr/bin/env bash

source read-secrets.sh
yum install -y postgresql-libs postgresql postgresql-devel
pip install -r requirements.txt
