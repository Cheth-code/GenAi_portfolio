#!/bin/bash

set -a
source .env
set +a
rq worker --with-scheduler --url redis://valkey:6379