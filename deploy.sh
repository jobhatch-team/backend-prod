#!/bin/bash

# Deployment script for Vercel
echo "🚀 Starting Vercel deployment..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Clean up any previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf .vercel

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment completed!"
echo "📋 Don't forget to:"
echo "   1. Set environment variables in Vercel dashboard"
echo "   2. Update frontend CORS settings"
echo "   3. Test all API endpoints" 