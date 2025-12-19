import sys
import os

print("Python Executable:", sys.executable)
print("CWD:", os.getcwd())
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))
print("sys.path:", sys.path)

try:
    import ceylonai_next

    print("Successfully imported ceylonai_next")
    print("ceylonai_next file:", ceylonai_next.__file__)
except ImportError as e:
    print("Failed to import ceylonai_next:", e)

try:
    from ceylonai_next import ceylonai_next as rust_module

    print("Successfully imported ceylonai_next.ceylonai_next")
    print("rust_module:", rust_module)
except ImportError as e:
    print("Failed to import ceylonai_next.ceylonai_next:", e)
