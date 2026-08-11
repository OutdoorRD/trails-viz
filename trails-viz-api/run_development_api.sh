#!/usr/bin/env bash

# Setup script to quickly re-start development backend
# https://github.com/OutdoorRD/trails-viz/wiki/Development#2-dashboard-backend-setup

# TODO: Enter variables here or run with `read -rp` commands below
CONDA_ENV="ENTER CONDA ENV HERE"
TRAILS_VIZ_DATA="ENTER DATA PATH HERE"
GCP_CREDS_PATH="ENTER GCP BUCKET PATH HERE"

# read -rp "Enter conda env name: " CONDA_ENV
# read -rp "Enter path to trails-viz-data repo (with trailing /): " TRAILS_VIZ_DATA
# read -rp "Enter path to gcp_bucket_credentials.json: " GCP_CREDS_PATH

source "$(conda info --base)/etc/profile.d/conda.sh"

conda activate $CONDA_ENV
conda env config vars set FLASK_APP="trailsvizapi"
conda env config vars set FLASK_ENV="development"
conda env config vars set DATA_FILES_ROOT="$TRAILS_VIZ_DATA"
conda env config vars set GOOGLE_APPLICATION_CREDENTIALS="$GCP_CREDS_PATH"

conda deactivate
conda activate $CONDA_ENV

flask run
