import os

def check_current_directory():
    current_directory = os.getcwd()
    try:
        with os.scandir(current_directory) as entries:
            for entry in entries:
  
                if 'data.db' in entry.name:
                    print('Ok')
    except OSError as e:
        print(f"Error: {e}")

# Test the function
check_current_directory()
