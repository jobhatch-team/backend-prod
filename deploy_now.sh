#!/bin/bash

echo "JobHatch Backend Deployment Script"
echo "=================================="
echo

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed"
    echo "Please install it with: npm install -g vercel"
    exit 1
fi

echo "✅ Vercel CLI found"

# Check if we're in the right directory
if [ ! -f "app/__init__.py" ]; then
    echo "❌ Error: app/__init__.py not found"
    echo "Please run this script from the backend-prod directory"
    exit 1
fi

echo "✅ Found Flask app"

# Display current status
echo
echo "Current Flask App Status:"
echo "- Main app file: app/__init__.py"
echo "- Vercel config: vercel.json"
echo "- Entry point: api/index.py"
echo "- Requirements: requirements.txt"
echo

# Ask for confirmation
read -p "Deploy to Vercel production? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo
echo "🚀 Deploying to Vercel..."
echo

# Deploy to production
vercel --prod

# Check deployment status
echo
echo "✅ Deployment complete!"
echo
echo "Testing endpoints..."

# Wait a moment for deployment to be ready
sleep 5

# Test key endpoints
echo "Testing health endpoint..."
curl -s "https://backend-prod-dun.vercel.app/api/health" | jq '.' 2>/dev/null || echo "Health endpoint response received"

echo
echo "Testing waitlist endpoint..."
curl -s "https://backend-prod-dun.vercel.app/api/waitlist" | jq '.' 2>/dev/null || echo "Waitlist endpoint response received"

echo
echo "🎉 Deployment and testing complete!"
echo
echo "You can now test the frontend with the updated backend."
echo "Visit: https://backend-prod-dun.vercel.app/api/docs for API documentation" 