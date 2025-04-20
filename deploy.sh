#!/bin/bash
# Simple script to deploy to GitHub Pages

# Exit on error
set -e

# Build the site
echo "Building site..."
bunx --bun astro build

# Create or use the gh-pages branch
echo "Setting up gh-pages branch..."
git branch -D gh-pages 2>/dev/null || true
git checkout -b gh-pages

# Remove everything except the dist folder
echo "Cleaning up repository for deployment..."
find . -maxdepth 1 -not -path "./dist" -not -path "./.git" -not -path "." -exec rm -rf {} \;

# Move dist contents to root
echo "Moving built files to repository root..."
mv dist/* .
rmdir dist

# Add all files
echo "Adding files to git..."
git add .

# Commit
echo "Committing changes..."
git commit -m "Deploy to GitHub Pages"

# Push to GitHub
echo "Pushing to GitHub..."
git push -f origin gh-pages

# Return to main branch
echo "Returning to main branch..."
git checkout main

echo "Deployment complete! Your site should be available at: https://vehas.github.io/thai-o-net-llm-test/"
