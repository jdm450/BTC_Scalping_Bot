import json
import os

# Define the path to your JSON file
HISTORY_FILE = 'trading_history.json'

def load_trading_history(file_path):
    """
    Loads trading history from the specified JSON file.
    Returns the data as a dictionary.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    try:
        with open(file_path, 'r') as f:
            history = json.load(f)
        return history
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading the file: {e}")
        return None

def save_trading_history(file_path, data):
    """
    Saves the provided data dictionary to the specified JSON file.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully updated '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def delete_last_entry(file_path, section):
    """
    Deletes the last entry from the specified section ('transactions' or 'portfolio_history').

    Parameters:
    - file_path: Path to the JSON file.
    - section: The section from which to delete the last entry.
    """
    # Load existing history
    history = load_trading_history(file_path)
    if history is None:
        return

    # Check if the section exists
    if section not in history:
        print(f"Error: The section '{section}' does not exist in the JSON file.")
        return

    # Check if the section is a list
    if not isinstance(history[section], list):
        print(f"Error: The section '{section}' is not a list.")
        return

    # Check if the section is not empty
    if len(history[section]) == 0:
        print(f"The section '{section}' is already empty. Nothing to delete.")
        return

    # Delete the last entry
    removed_entry = history[section].pop()
    print(f"Removed the last entry from '{section}':")
    print(json.dumps(removed_entry, indent=4))

    # Save the updated history
    save_trading_history(file_path, history)

def main():
    """
    Main function to interact with the user and perform deletion.
    """
    print("=== Delete Last Entry from Trading History ===")
    print("Choose the section from which you want to delete the last entry:")
    print("1. transactions")
    print("2. portfolio_history")
    print("3. Exit")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == '1':
        delete_last_entry(HISTORY_FILE, 'transactions')
    elif choice == '2':
        delete_last_entry(HISTORY_FILE, 'portfolio_history')
    elif choice == '3':
        print("Exiting the script.")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
