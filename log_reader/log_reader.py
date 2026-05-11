with open('sample.log', 'r') as f:
    error_dict = {}
    count = 0
    for line in f:
        if 'ERROR' in line:
            count += 1
            message = line.split('ERROR', 1)[1].strip()
            if message in error_dict:
                error_dict[message] += 1
            else:
                error_dict[message] = 1

    print(f"Total error occurrences: {count}")
    for message, count in error_dict.items():
        print(f" - {message} (x{count})")