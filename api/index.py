import sys
import traceback

try:
    from .app import app
    print("Successfully imported Flask app")
except Exception as e:
    print(f"Error importing Flask app: {e}")
    traceback.print_exc()
    sys.exit(1)

# This file serves as the entry point for Vercel deployment
# Vercel requires the app to be exposed directly as a module-level variable
