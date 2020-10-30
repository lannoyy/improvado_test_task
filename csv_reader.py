import csv

def get_key(row:str) -> str:
    output = ""
    for element in row:
        if element.isalpha():
            output+= element
    return output

def calculate_row(first_row:str, second_row:str) -> str:
    output = []
    for first_element, second_element in zip(first_row.split(','), second_row.split(',')):
        if first_element.isdigit() and second_element.isdigit():
            output.append(str(int(first_element) + int(second_element)))
        else:
            output.append(first_element)
    return ','.join(output)

def delete_row(data, need_to_delete):
    count = 0
    for num in need_to_delete:
        del data[num-count]
        count += 1 

def validate_row(row, header):
    if len(row.split(',')) != len(header.split(',')):
        return -1
    return 1

def purge_data(data, header):
    need_to_delete = []
    bad_data = []
    for row in data:
        if validate_row(row, header) == -1:
            need_to_delete.append(data.index(row))
            bad_data.append(row)
    delete_row(data, need_to_delete)
    return bad_data

def print_into_file(file, output, header = None):
    with open(file, 'w') as output_file:
        if header:
            output_file.write(header + '\n')
        for row in output[:-1]:
            output_file.write(row +'\n')
        output_file.write(output[-1])


with open('csv_data_1.csv') as csvfile:
    header = csvfile.readline()[:-1]
    data = csvfile.read().split('\n')
    output = []
    need_to_delete = [0]
    bad_data = purge_data(data, header)
    while True:
        first_row = data[0]
        for index, second_row in enumerate(data[1:], 1):
            if get_key(first_row) == get_key(second_row):
                first_row = calculate_row(first_row, second_row)
                need_to_delete.append(index)
        output.append(first_row)
        delete_row(data, need_to_delete)
        need_to_delete = [0]
        if data:
            if len(data) <= 1:
                output.append(data[0])
                break
        else:
            break
    print_into_file('csv_output_1.csv', output, header)
    print_into_file('bad_data_output_1.csv', bad_data)