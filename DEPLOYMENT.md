# JSAS Deployment Guide

Run these commands in your terminal to deploy the Japan Safety Alert System (JSAS) to Google Cloud Platform.

## 1. Initial Setup
Set your project details.
```bash
# Set your variables
export PROJECT_ID="virustotal-lab"
export REGION="asia-southeast1"
export REPO_NAME="dom-jsas-repo"

# Authenticate and set project
gcloud auth login
gcloud config set project $PROJECT_ID
```

## 2. Enable APIs
Enable the necessary services.
```bash
gcloud services enable \
  firestore.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com
```

## 3. Configure Resources

### Create Firestore Database
(If you haven't already created one via Console)
```bash
gcloud firestore databases create --location=$REGION --type=firestore-native
```

### Setup Secrets
Store your Telegram Bot Token safely.
```bash
# Create the secret
gcloud secrets create TELEGRAM_TOKEN --replication-policy="automatic"

# Add the token value (Replace YOUR_TOKEN_HERE)
echo -n "YOUR_TOKEN_HERE" | gcloud secrets versions add TELEGRAM_TOKEN --data-file=-
```

## 4. Deploy Backend (Cloud Function)

### Grant Permissions
The default service account needs access to Secret Manager and Firestore.
```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Secret Manager Access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor

# Firestore Access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role=roles/datastore.user
```

### Deploy the Bot
This function polls for quakes.
```bash
gcloud functions deploy jsas-bot \
    --gen2 \
    --runtime=python310 \
    --region=$REGION \
    --source=. \
    --entry-point=poll_quakes \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets=TELEGRAM_TOKEN=projects/$PROJECT_ID/secrets/TELEGRAM_TOKEN:latest
```
*Note: We use `--allow-unauthenticated` so Cloud Scheduler can trigger it easily, but for production security, you should configure a service account and OIDC token.*

### Configure Cloud Scheduler
Trigger the bot every minute.
```bash
# Get the function URL
FUNCTION_URL=$(gcloud functions describe jsas-bot --region=$REGION --format='value(serviceConfig.uri)')

# Create the job
gcloud scheduler jobs create http jsas-poller \
    --location=$REGION \
    --schedule="* * * * *" \
    --uri=$FUNCTION_URL \
    --http-method=GET
```

## 5. Deploy Frontend (Cloud Run)

### Create Artifact Repository
```bash
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="JSAS Repository"
```

### Build and Deploy Container
```bash
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/jsas-dashboard .

gcloud run deploy jsas-dashboard \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/jsas-dashboard \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080
```

## 6. Verification
Get your dashboard URL:
```bash
gcloud run services describe jsas-dashboard --region=$REGION --format='value(status.url)'
```
Visit the URL to see your dashboard!
