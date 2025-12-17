#!/bin/bash

# Configuration - EDIT THESE BEFORE RUNNING
PROJECT_ID="virustotal-lab"
REGION="asia-southeast1"
REPO_NAME="dom-jsas-repo"
IMAGE_NAME="jsas-dashboard"

# Note: TELEGRAM_TOKEN must be in Secret Manager
# Renamed bot.py to main.py to satisfy Cloud Functions requirement

echo "Granting Secret Manager access to default service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor

echo "Granting Firestore access to default service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role=roles/datastore.user

gcloud functions deploy jsas-bot \
    --gen2 \
    --runtime=python310 \
    --region=$REGION \
    --source=. \
    --entry-point=poll_quakes \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets=TELEGRAM_TOKEN=projects/$PROJECT_ID/secrets/TELEGRAM_TOKEN:latest

echo "Building and Deploying Streamlit Dashboard..."
gcloud artifacts repositories create $REPO_NAME --repository-format=docker \
    --location=$REGION --description="JSAS Repository" || true

gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME .

gcloud run deploy jsas-dashboard \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080
