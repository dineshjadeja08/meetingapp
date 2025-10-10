#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_ecr.sh <AWS_ACCOUNT_ID> <AWS_REGION> [REPO_NAME] [LOCAL_IMAGE] [IMAGE_TAG]
AWS_ACCOUNT_ID=${1:-}
AWS_REGION=${2:-us-east-1}
REPO_NAME=${3:-meetingapp-web}
LOCAL_IMAGE=${4:-meetingapp-web:latest}
IMAGE_TAG=${5:-latest}

if [ -z "$AWS_ACCOUNT_ID" ]; then
  echo "Usage: $0 <AWS_ACCOUNT_ID> <AWS_REGION> [REPO_NAME] [LOCAL_IMAGE] [IMAGE_TAG]"
  exit 1
fi

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME"
FULL_TAG="$ECR_URI:$IMAGE_TAG"

echo "Building Docker image $LOCAL_IMAGE"
docker build -t "$LOCAL_IMAGE" .

echo "Ensure ECR repository exists..."
if ! aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$AWS_REGION" >/dev/null 2>&1; then
  echo "Repository not found, creating: $REPO_NAME"
  aws ecr create-repository --repository-name "$REPO_NAME" --region "$AWS_REGION" >/dev/null
fi

echo "Logging in to ECR $AWS_REGION"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "Tagging image: $LOCAL_IMAGE -> $FULL_TAG"
docker tag "$LOCAL_IMAGE" "$FULL_TAG"

echo "Pushing image to ECR: $FULL_TAG"
docker push "$FULL_TAG"

echo "Image pushed: $FULL_TAG"
