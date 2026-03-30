from pathlib import Path

current_dir = Path.cwd()
print(f"Current working directory: {current_dir}")

parent = current_dir.parent
grandparent = parent.parent
print(f"Parent directory: {parent}")
print(f"Grandparent directory: {grandparent}")

for item in current_dir.iterdir():
    if item.is_dir():
        print(f"Directory: {item.name}")


for item in current_dir.iterdir():
    if item.is_file():
        print(f"File: {item.name}")


for item in current_dir.iterdir():
    if item.suffix == ".py":
        print(f"Python file: {item.name}")

for item in current_dir.rglob("*"):
    print(f"Item: {item.name}")