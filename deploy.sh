#!/bin/bash
set -e

# GCP Deployment Script for AI Pathway Tool
# Usage: ./deploy.sh [backend|frontend|all]

PROJECT_ID="ai-pathway-486221"
REGION="us-central1"
ARTIFACT_REPO="ai-pathway"
BUCKET_NAME="ai-pathway-data-${PROJECT_ID}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Set project and enable APIs
setup_gcp() {
    log_info "Setting GCP project to ${PROJECT_ID}..."
    gcloud config set project ${PROJECT_ID}

    log_info "Enabling required APIs..."
    gcloud services enable \
        run.googleapis.com \
        artifactregistry.googleapis.com \
        cloudbuild.googleapis.com \
        storage.googleapis.com \
        aiplatform.googleapis.com
}

# Step 2: Create Artifact Registry repository
create_artifact_registry() {
    log_info "Creating Artifact Registry repository..."
    gcloud artifacts repositories create ${ARTIFACT_REPO} \
        --repository-format=docker \
        --location=${REGION} \
        --description="AI Pathway Docker images" \
        2>/dev/null || log_warn "Repository already exists"
}

# Step 3: Create Cloud Storage bucket and upload data
setup_storage() {
    log_info "Creating Cloud Storage bucket..."
    gsutil mb -l ${REGION} gs://${BUCKET_NAME} 2>/dev/null || log_warn "Bucket already exists"

    log_info "Uploading data files..."
    if [ -f "backend/app/data/ontology.json" ]; then
        gsutil cp backend/app/data/ontology.json gs://${BUCKET_NAME}/
    fi
    if [ -d "backend/app/data/profiles" ]; then
        gsutil -m cp -r backend/app/data/profiles gs://${BUCKET_NAME}/
    fi
}

# Step 4: Deploy Backend
deploy_backend() {
    log_info "Building and deploying backend..."
    cd backend

    # Build and push image
    gcloud builds submit \
        --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/backend:v1

    # Deploy to Cloud Run
    gcloud run deploy ai-pathway-backend \
        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/backend:v1 \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --set-env-vars "LLM_PROVIDER=vertex,GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION}"

    cd ..

    # Get backend URL
    BACKEND_URL=$(gcloud run services describe ai-pathway-backend --region ${REGION} --format 'value(status.url)')
    log_info "Backend deployed at: ${BACKEND_URL}"
    echo "${BACKEND_URL}" > .backend_url
}

# Step 5: Deploy Frontend
deploy_frontend() {
    if [ -f ".backend_url" ]; then
        BACKEND_URL=$(cat .backend_url)
    else
        BACKEND_URL=$(gcloud run services describe ai-pathway-backend --region ${REGION} --format 'value(status.url)' 2>/dev/null || echo "")
    fi

    if [ -z "${BACKEND_URL}" ]; then
        log_error "Backend URL not found. Deploy backend first."
        exit 1
    fi

    log_info "Building and deploying frontend..."
    log_info "Backend URL: ${BACKEND_URL}"

    cd frontend

    # Build and push image
    gcloud builds submit \
        --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/frontend:v1

    # Deploy to Cloud Run
    gcloud run deploy ai-pathway-frontend \
        --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/frontend:v1 \
        --region ${REGION} \
        --allow-unauthenticated \
        --set-env-vars "BACKEND_URL=${BACKEND_URL}"

    cd ..

    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe ai-pathway-frontend --region ${REGION} --format 'value(status.url)')
    log_info "Frontend deployed at: ${FRONTEND_URL}"

    # Update backend CORS
    log_info "Updating backend CORS settings..."
    gcloud run services update ai-pathway-backend \
        --region ${REGION} \
        --update-env-vars "CORS_ORIGINS=${FRONTEND_URL}"
}

# Show deployment URLs
show_urls() {
    log_info "Deployment URLs:"
    BACKEND_URL=$(gcloud run services describe ai-pathway-backend --region ${REGION} --format 'value(status.url)' 2>/dev/null || echo "Not deployed")
    FRONTEND_URL=$(gcloud run services describe ai-pathway-frontend --region ${REGION} --format 'value(status.url)' 2>/dev/null || echo "Not deployed")
    echo "  Backend:  ${BACKEND_URL}"
    echo "  Frontend: ${FRONTEND_URL}"
}

# Main
case "${1:-all}" in
    setup)
        setup_gcp
        create_artifact_registry
        setup_storage
        ;;
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        setup_gcp
        create_artifact_registry
        setup_storage
        deploy_backend
        deploy_frontend
        show_urls
        ;;
    urls)
        show_urls
        ;;
    *)
        echo "Usage: $0 [setup|backend|frontend|all|urls]"
        echo "  setup    - Enable APIs and create resources"
        echo "  backend  - Deploy backend only"
        echo "  frontend - Deploy frontend only"
        echo "  all      - Full deployment (default)"
        echo "  urls     - Show deployment URLs"
        exit 1
        ;;
esac

log_info "Done!"
