import openmeteo_sdk
import inspect
import sys

# Print all available modules and classes in openmeteo_sdk
print("Available in openmeteo_sdk:")
for name in dir(openmeteo_sdk):
    if not name.startswith('_'):  # Skip private attributes
        print(f"- {name}")
        
        # If it's a module, explore it further
        attr = getattr(openmeteo_sdk, name)
        if inspect.ismodule(attr):
            print(f"  Module contents of {name}:")
            for subname in dir(attr):
                if not subname.startswith('_'):
                    print(f"  - {subname}")

# Print the path where openmeteo_sdk is installed
print(f"\nOpenMeteo SDK is installed at: {openmeteo_sdk.__file__}")

# Print the Python path
print("\nPython path:")
for path in sys.path:
    print(f"- {path}")

