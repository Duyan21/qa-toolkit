def log_reader(filePath):
    error_dict = {}
    with open(filePath, 'r', encoding='utf-8') as f:
        count = 0
        for line in f:
            if 'ERROR' in line:
                count += 1
                message = line.split('ERROR', 1)[1].strip()
                if message in error_dict:
                    error_dict[message] += 1
                else:
                    error_dict[message] = 1
    return error_dict

if __name__ == "__main__":
    result = log_reader('sample.log')
    total_errors = sum(result.values())
    print(f"Total error occurrences: {total_errors}")
    for message, count in result.items():
        print(f" - {message} (x{count})")