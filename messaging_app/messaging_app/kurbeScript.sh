#!/bin/bash

# kurbeScript.sh - Sets up a local Kubernetes cluster using Minikube

# Check if minikube is installed
if ! command -v minikube &> /dev/null
then
    echo "❌ Minikube is not installed. Please install Minikube before running this script."
    echo "🔗 Installation guide: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null
then
    echo "❌ kubectl is not installed. Please install kubectl before running this script."
    echo "🔗 Installation guide: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Start the Minikube cluster
echo "🚀 Starting Minikube..."
minikube start

# Wait for Minikube to be ready
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Minikube cluster."
    exit 1
fi

# Verify that the cluster is running
echo "🔍 Verifying cluster status..."
kubectl cluster-info

# Get available pods
echo "📦 Listing pods in all namespaces..."
kubectl get pods --all-namespaces

echo "✅ Kubernetes local cluster setup complete!"
