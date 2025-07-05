import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the application"""
    try:
        # Import the GUI module
        from gui import MiningStopeDesignApp

        # Create and run the application
        app = MiningStopeDesignApp()
        app.run()

    except ImportError as e:
        error_msg = f"Failed to import required modules: {e}"
        print(error_msg)
        if 'tkinter' in sys.modules:
            messagebox.showerror("Import Error", error_msg)
        sys.exit(1)

    except Exception as e:
        error_msg = f"Application failed to start: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        if 'tkinter' in sys.modules:
            messagebox.showerror("Application Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()