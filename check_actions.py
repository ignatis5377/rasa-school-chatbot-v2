import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

print("Attempting to import actions...")
try:
    import actions.actions
    print("SUCCESS: actions.actions imported correctly.")
except Exception as e:
    print(f"FAILURE: Could not import actions.actions. Error: {e}")
except SystemExit as se:
    print(f"FAILURE: SystemExit during import (maybe sys.exit() called?). Error: {se}")
