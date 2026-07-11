import subprocess

tests = [
    "Tests/test_search.py",
]

for test in tests:
    print(f"\nRunning {test}")
    print("-" * 40)

    result = subprocess.run(
        ["python", test],
        text=True
    )

    if result.returncode == 0:
        print("PASS")
    else:
        print("FAIL")