#!/bin/bash

if [[ ${ENVIRONMENT} == "prod" ]]; then
    #gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8007
    uvicorn main:app --workers 8 --host 0.0.0.0 --port 8007
else
    uvicorn main:app --host 0.0.0.0 --port 8007 --reload
fi
