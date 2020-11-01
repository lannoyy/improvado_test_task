import json
import sys
import argparse


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lvl', nargs=1)
    parser.add_argument('-i', '--input', nargs='+')
    parser.add_argument('--output', nargs=1)
    return parser


def printIntoFile(header, output, file_name):
    with open(file_name, 'w') as output_file:
        if header:
            output_file.write("\t".join(header) + "\n")
        for row in output[:-1]:
            output_file.write("\t".join(map(str, row)) + "\n")
        output_file.write("\t".join(map(str, output[-1])))
    print("Ready")


def createCsvReader(file_name):
    with open(file_name) as csv_file:
        header = csv_file.readline()[:-1].split(",")
        data = csv_file.read().split("\n")
        count = 0
        count_keys = 0
        count_num = 0
        for element in header:
            if element.startswith("D"):
                count_keys += 1
            elif element.startswith("M"):
                count_num += 1
        for index, row in enumerate(data):
            if len(row.split(",")) != len(header):
                print(f"Bad row {row}")
                del data[index - count]
                count += 1
        nums = [[0 for j in range(count_num)] for i in range(len(data))]
        keys = [[0 for j in range(count_keys)] for i in range(len(data))]
        for index, element in enumerate(data):
            count = 0
            for key in header:
                if key.startswith("M"):
                    nums[index][int(key[1:]) - 1] \
                        = int(element.split(",")[count])
                elif key.startswith("D"):
                    keys[index][int(key[1:]) - 1] \
                        = element.split(",")[count]
                count += 1
        return header, nums, keys


def createJsonReader(file_name):
    with open(file_name) as json_file:
        count_keys = 0
        count_num = 0
        data = json.loads(json_file.read())["fields"]
        header = list(data[0].keys())
        for key in data[0].keys():
            if key.startswith("D"):
                count_keys += 1
            elif key.startswith("M"):
                count_num += 1
        nums = [[0 for j in range(count_num)] for i in range(len(data))]
        keys = [[0 for j in range(count_keys)] for i in range(len(data))]
        for index, element in enumerate(data):
            for key, value in element.items():
                if len(element.values()) == len(header):
                    if key.startswith("M"):
                        nums[index][int(key[1:]) - 1] = value
                    if key.startswith("D"):
                        keys[index][int(key[1:]) - 1] = value
        return header, nums, keys


class Reader():

    def __init__(self, file_name):
        if file_name.endswith(".csv"):
            self.header, self.nums, self.keys = createCsvReader(file_name)
            self.type = 'csv'
        elif file_name.endswith(".json"):
            self.header, self.nums, self.keys = createJsonReader(file_name)
            self.type = 'json'


def standartisation(*args):
    max_num = 0
    for reader in args:
        if len(reader.nums[0]) > max_num:
            max_num = len(reader.nums[0])
    max_key = len(reader.keys[0])
    for reader in args:
        if len(reader.nums[0]) != max_num:
            difference = max_num - len(reader.nums[0])
            for row in reader.nums:
                row += [0 for i in range(difference)]
    return max_num, max_key


def uniteData(level, max_key, max_num, *args):
    data = {"keys": [], "nums": [], "header": []}
    for reader in args:
        data["keys"] += reader.keys
        data["nums"] += reader.nums
    for i in range(max_key):
        data["header"].append(f"D{i + 1}")
    for i in range(max_num):
        if level == 'basic':
            data["header"].append(f"M{i + 1}")
        elif level == 'advanced':
            data["header"].append(f"MS{i + 1}")
    return data


def deleteRows(need_to_delete, data):
    count = 0
    for num in need_to_delete:
        del data["nums"][num-count]
        del data["keys"][num-count]
        count += 1


def calculateAdvanced(data):
    need_to_delete = [0]
    output = []
    while True:
        if len(data["nums"]) <= 1:
            output.append(data["keys"][0] + data["nums"][0])
            break
        first_num = data["nums"][0]
        first_key = data["keys"][0]
        for index, second_num in enumerate(data["nums"][1:], 1):
            second_key = data["keys"][index]
            if first_key == second_key:
                need_to_delete.append(index)
                first_num = [i + j for i, j in zip(first_num, second_num)]
        output.append(first_key + first_num)
        deleteRows(need_to_delete, data)
        need_to_delete = [0]
        if not data["nums"]:
            break
    return sorted(output)


def calculateBasic(data):
    need_to_delete = [0]
    output = []
    while True:
        if len(data["nums"]) <= 1:
            output.append(data["keys"][0] + data["nums"][0])
            break
        first_num = data["nums"][0]
        first_key = data["keys"][0]
        output.append(first_key + first_num)
        deleteRows(need_to_delete, data)
        need_to_delete = [0]
        if not data["nums"]:
            break
    return sorted(output)


def main(level, input_files, output_file):
    print("Start")
    files_array = []
    for file in input_files:
        files_array.append(Reader(file))
    max_num, max_key = standartisation(*files_array)
    data = uniteData(level, max_key, max_num, *files_array)
    if level == 'advanced':
        output = calculateAdvanced(data)
    elif level == 'basic':
        output = calculateBasic(data)
    else:
        print("Bad arguments")
        quit()
    printIntoFile(data["header"], output, output_file)


if __name__ == "__main__":
    parser = createParser()
    console = parser.parse_args(sys.argv[1:])
    main(console.lvl[0], console.input, console.output[0])
