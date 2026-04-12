#!/bin/bash

# Setup Stitch MCP script
# This script generates .env credentials and refreshes the stitch MCP connection

echo "🔧 Setting up Stitch MCP..."


# Set Google Cloud project ID
PROJECT_ID=my-stitch-devops

# Generate access token using gcloud
echo "🔑 Generating access token..."
TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to generate access token"
    echo "Make sure you're authenticated with gcloud"
    exit 1
fi

# Create .env file
echo "📝 Creating .env file..."
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" > .env
echo "STITCH_ACCESS_TOKEN=$TOKEN" >> .env

echo "✅ Secrets generated in .env"

# Set path to claude command
CLAUDE_CMD="/Users/moya/.claude/local/claude"

# Remove existing stitch MCP server if it exists
echo "🗑️  Removing existing stitch MCP server (if exists)..."
$CLAUDE_CMD mcp remove stitch 2>/dev/null || true

# Add stitch MCP server with new credentials
echo "➕ Adding stitch MCP server..."
$CLAUDE_CMD mcp add stitch \
  --transport http https://stitch.googleapis.com/mcp \
  --header "Authorization: Bearer $TOKEN" \
  --header "X-Goog-User-Project: $PROJECT_ID" \
  -s user

# Check MCP server status
echo ""
echo "📊 MCP Server Status:"
$CLAUDE_CMD mcp list

echo ""
echo "✨ Setup complete! Try using stitch tools now."
