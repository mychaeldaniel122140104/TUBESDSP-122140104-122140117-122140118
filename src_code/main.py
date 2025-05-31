
import sys
import traceback
from tkinter import messagebox

try:
    from gui import RespirasiRPPGApp
except ImportError as e:
    print("Error: Failed to import required modules.")
    print(f"Details: {e}")
    print("\nPlease make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """
    Main function untuk menjalankan aplikasi.
    
    Includes error handling untuk graceful exit jika terjadi error
    pada inisialisasi atau runtime.
    """
    try:
        print("Starting Real-time rPPG and Respiration Rate Tracker...")
        print("Initializing application components...")
        
        # Inisialisasi aplikasi
        app = RespirasiRPPGApp()
        
        print("Application initialized successfully!")
        print("Starting GUI...")
        
        # Jalankan aplikasi
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user (Ctrl+C)")
        
    except Exception as e:
        error_msg = f"Critical error occurred: {str(e)}"
        print(f"\n{error_msg}")
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            messagebox.showerror("Critical Error", 
                               f"{error_msg}\n\nSee console for full details.")
        except:
            pass  # GUI might not be available
        
        sys.exit(1)
    
    finally:
        print("Cleaning up resources...")
        print("Application closed.")


if __name__ == "__main__":
    main()