#!/bin/bash
# Ubuyu Marketplace - Start Script

echo "🍬 Ubuyu Marketplace - Starting Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Start the application
echo ""
echo "✅ Server starting on http://localhost:5000"
echo ""
echo "Default Pages:"
echo "  - Home: http://localhost:5000"
echo "  - Products: http://localhost:5000/products/catalog"
echo "  - Register: http://localhost:5000/auth/register"
echo "  - Login: http://localhost:5000/auth/login"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
