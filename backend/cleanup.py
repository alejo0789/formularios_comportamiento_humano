import os
import glob
import sys

def clean_data():
    # Define the data directory
    # Assumes this script is in the 'backend' folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    print("="*60)
    print("WARNING: SYSTEM DATA CLEANUP")
    print("="*60)
    print(f"Directory to clean: {data_dir}")
    print("This will PERMANENTLY DELETE all user sessions and survey responses.")
    print("This action cannot be undone.")
    print("="*60)

    # Ask for confirmation
    confirm = input("Type 'DELETE' to confirm and proceed: ")

    if confirm != "DELETE":
        print("\nCleanup cancelled. No files were deleted.")
        return

    if not os.path.exists(data_dir):
        print(f"\nDirectory not found: {data_dir}")
        return

    # Files to delete: all .json files in the data directory
    # We use glob to match patterns
    files = glob.glob(os.path.join(data_dir, "*.json"))
    
    if not files:
        print("\nNo data files found to delete.")
        return

    deleted_count = 0
    print("\nDeleting files...")
    
    for file_path in files:
        try:
            os.remove(file_path)
            print(f" - Deleted: {os.path.basename(file_path)}")
            deleted_count += 1
        except Exception as e:
            print(f" ! Error deleting {os.path.basename(file_path)}: {e}")

    print("-" * 60)
    print(f"Cleanup complete. {deleted_count} files deleted.")
    print("The system is now clean and ready for delivery.")

if __name__ == "__main__":
    clean_data()
