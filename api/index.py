import sys
import traceback

try:
    # Import the main Flask app
    from .app import app
    print("Successfully imported main Flask app")
except Exception as e:
    print(f"Error importing main app: {e}")
    traceback.print_exc()
    sys.exit(1)

# This file serves as the entry point for Vercel deployment
# Vercel requires the app to be exposed directly as a module-level variable
