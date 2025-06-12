from functions.run_python import run_python_file

print("Test 1 - Run main.py:")
print(run_python_file("calculator", "main.py"))
print("\n" + "="*40 + "\n")

print("Test 2 - Run tests.py:")
print(run_python_file("calculator", "tests.py"))
print("\n" + "="*40 + "\n")

print("Test 3 - Try escaping working directory:")
print(run_python_file("calculator", "../main.py"))
print("\n" + "="*40 + "\n")

print("Test 4 - Run nonexistent file:")
print(run_python_file("calculator", "nonexistent.py"))
print("\n" + "="*40 + "\n")
