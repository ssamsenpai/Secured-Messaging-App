#!/bin/bash
# Script to run the Secured Messenger App

echo "🔐 Starting Secured Messenger App..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "🚀 Launching Streamlit application..."
echo "📱 Open your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
