#!/bin/bash
# Test runner script for AI Customer Support System

echo "🧪 Running AI Customer Support System Tests..."
echo "=============================================="

# Navigate to backend directory
cd backend

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements-test.txt

# Run tests with coverage
echo "🔍 Running unit tests..."
python -m pytest test_main.py -v --tb=short

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "🎉 System is ready for deployment!"
else
    echo "❌ Some tests failed!"
    echo "🔧 Please fix failing tests before deployment."
    exit 1
fi