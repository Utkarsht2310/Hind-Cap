#!/bin/bash
# Build script for Render/Railway deployment
echo "Installing FFmpeg..."
apt-get update
apt-get install -y ffmpeg
echo "FFmpeg installed successfully!"

