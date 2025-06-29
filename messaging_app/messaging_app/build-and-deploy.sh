#!/bin/bash

# Step 1: Use Minikube's Docker daemon
echo "🔁 Switching to Minikube Docker environment..."
eval $(minikube docker-env)

# Step 2: Build the Docker image inside Minikube
echo "🐳 Building Docker image 'django-messaging:latest'..."
docker build -t django-messaging:latest .

# Step 3: Ensure deployment.yaml is using local image
echo "📝 Make sure 'deployment.yaml' uses: image: django-messaging:latest"

# Step 4: Delete existing deployment (if any) and apply the new one
echo "🚀 Re-deploying to Kubernetes..."
kubectl delete deployment django-messaging --ignore-not-found
kubectl apply -f deployment.yaml

# Step 5: Watch pod status
echo "📦 Checking pod status..."
kubectl get pods -w
