import sys
import traceback

try:
    # Import the main app now that we know basic deployment works
    from .app import app
    print("Successfully imported main Flask app")
except Exception as e:
    print(f"Error importing main app: {e}")
    traceback.print_exc()
    try:
        # Fallback to test app if main app fails
        from .test_app import app
        print("Successfully imported test Flask app as fallback")
    except Exception as e2:
        print(f"Error importing test app: {e2}")
        traceback.print_exc()
        sys.exit(1)

# This file serves as the entry point for Vercel deployment
# Vercel requires the app to be exposed directly as a module-level variable
