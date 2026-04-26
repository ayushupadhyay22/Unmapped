#!/bin/bash
# Make this script executable with: chmod +x run.sh

#echo "Installing requirements..."
#pip install -r requirements.txt

#echo "Initializing Data..."
# Run the DB script from the project root
#python scripts/init_db.py

# Automatically activate the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Starting Backend (FastAPI)..."
# Run uvicorn from the root directory so the "backend" folder acts as a module. 
# This prevents the "attempted relative import" error in main.py.
python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend (Streamlit)..."
# Run streamlit (redirect stdin so it doesn't hang on the welcome email prompt)
< /dev/null python -m streamlit run frontend/app.py --server.headless true &
FRONTEND_PID=$!

echo "====================================="
echo "🌍 UNMAPPED is running!"
echo "📄 API Docs: http://localhost:8000/docs"
echo "🖥️ Frontend Dashboard: http://localhost:8501"
echo "====================================="
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C (SIGINT) to kill background processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT

# Wait for user interrupt
wait
