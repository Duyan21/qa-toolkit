import json


with open("file1.json", "r") as f1, open("file2.json", "r") as f2:
    data1 = json.load(f1)
    data2 = json.load(f2)
    missing_keys = []
    diff_values = []
    identical = []

    for key, value in data1.items():
        if key not in data2:
            missing_keys.append(key)
        elif data2[key] != value:
            diff_values.append((key, value, data2[key]))
        else:
            identical.append(key)

    print(f"Missing keys in file2: {len(missing_keys)}")
    for key in missing_keys:
        print(f" - {key}")

    print(f"\nDifferent values: {len(diff_values)}")
    for key, val1, val2 in diff_values:
        print(f" - {key}: file1='{val1}' vs file2='{val2}'")

    print(f"\nIdentical values: {len(identical)}")
    for key in identical:
        print(f" - {key}")
