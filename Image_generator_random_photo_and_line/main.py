import os
import glob
import random
import itertools
from os import listdir
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from random import randint
from os.path import isfile, join


def read_hyper_parameters(parameter_file_name):
    all_lines = []
    with open(parameter_file_name) as f:
        all_lines = [line.rstrip() for line in f]

    combinations_line = all_lines[0]
    combinations = int(combinations_line.split('=')[1].rstrip())

    drop_lines_line = all_lines[1]
    is_drop_lines_loc = str(drop_lines_line.split('= ')[1].rstrip())

    font_size_line = all_lines[11]
    font_size_local = int(font_size_line.split('=')[1].rstrip())

    font_color_line = all_lines[12]
    font_color_all = font_color_line.split('=')[1].rstrip()

    red = int(font_color_all.split(',')[0].rstrip())
    green = int(font_color_all.split(',')[1].rstrip())
    blue = int(font_color_all.split(',')[2].rstrip())

    start_x_line = all_lines[13]
    start_x_local = int(start_x_line.split('=')[1].rstrip())

    start_y_line = all_lines[14]
    start_y_local = int(start_y_line.split('=')[1].rstrip())

    line_gap_line = all_lines[15]
    line_gap_local = int(line_gap_line.split('=')[1].rstrip())

    font_name_line = all_lines[16]
    font_name_local = font_name_line.split('= ')[1].rstrip()

    return combinations, is_drop_lines_loc, font_size_local, red, green, blue, start_x_local, start_y_local, line_gap_local, font_name_local


def read_probability_parameters(parameter_file_name):
    all_lines = []
    remove_prob_local = []

    with open(parameter_file_name) as f:
        all_lines = [line.rstrip() for line in f]

    for i in range(3,10):
        remove_prob_local.append(int(all_lines[i].split('= ')[1].split('%')[0]))
    
    return remove_prob_local


def delete_from_local_folder(local_folder):
    files = glob.glob(local_folder + '*')

    for file in files:
        os.remove(file)


def list_of_photos(folder_path):
    all_photo_names = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

    if '.DS_Store' in all_photo_names:
        all_photo_names.remove('.DS_Store')
    
    return all_photo_names


def read_from_file(file_name):
    all_lines = []
    with open(file_name) as f:
        all_lines = [line.rstrip() for line in f]

    return all_lines


def fetch_all_lines(lines_path_local):
    all_line_files = [f for f in listdir(lines_path_local) if isfile(join(lines_path_local, f))]

    if '.DS_Store' in all_line_files:
        all_line_files.remove('.DS_Store')

    lines = []
    count = 0

    for line_files in all_line_files:
        file_name = lines_path + line_files
        line_from_file = read_from_file(file_name)

        if len(line_from_file) == 0:
            break
        
        count = count + 1
        lines.append(line_from_file)

    print(f'\nReading {count} files to fetch lines')
    print(f'Reading {count-1} probability lines')
    print(f'Drop random lines => {is_drop_lines}')
    return lines


def is_traditional_algorithm(possible_combination, process_combination):
    is_traditional = True

    if possible_combination <= 500000:
        return is_traditional

    if possible_combination/process_combination < 2:
        return is_traditional

    is_traditional = False

    return is_traditional


def make_smart_combination(photos_list, all_lines, process_combination):
    if process_combination < 0:
        raise Exception('\nCan not make negative combination')

    random_combinations = []
    
    for i in range(0, process_combination):
        while True:
            random_photo = photos_list[randint(0, len(photos_list)-1)]
            random_line = []
            random_line.append(random_photo)

            for lines in all_lines:
                random_line.append(lines[randint(0, len(lines)-1)])
        
            random_line_tuple = tuple(random_line)

            if not random_line_tuple in random_combinations:
                random_combinations.append(random_line_tuple)
                break

    return random_combinations


def make_traditional_combination(photos_list, lines, process_combination):
    list_for_combination = []
    list_for_combination.append(photos_list)

    for line in lines:
        list_for_combination.append(line)

    if process_combination < 0:
        raise Exception('\nCan not make negative combination')

    all_process_combinations = []
    all_possible_combinations = list(itertools.product(*list_for_combination))

    random_numbers = random.sample(range(len(all_possible_combinations)), process_combination)

    for random_number in random_numbers:
        all_process_combinations.append(all_possible_combinations[random_number])

    return all_process_combinations


def make_cumilitive_sum(size_of_image_items):
    highest_fall_count = size_of_image_items - 1

    sum_all_fall = 0
    for i in range(0, highest_fall_count):
        sum_all_fall = sum_all_fall + remove_probs[i]

    zero_fall_prob = 100-sum_all_fall

    if zero_fall_prob < 0:
        raise Exception('\nProbability to drop no line can not be less than zero')

    cumilitive_sum = []
    cumilitive_sum.append(zero_fall_prob)

    for i in range(0, highest_fall_count):
        cumilitive_sum.append(cumilitive_sum[i] + remove_probs[i])

    return cumilitive_sum


def random_fall(image_items):
    line_fall_count = 0

    cumilitive_sum = make_cumilitive_sum(len(image_items))
    random_numb = randint(0, 99)

    for i in range(len(cumilitive_sum)):
        if random_numb < cumilitive_sum[i]:
            line_fall_count = i
            break
    
    for i in range(0, line_fall_count):
        random_numb = randint(0, len(image_items)-1)
        del image_items[random_numb]
    
    return image_items


def write_in_picture(image_item, count):
    image_name = image_item[0]
    img = Image.open(f'input_folder/photos/{image_name}')
    font = ImageFont.truetype(f'input_folder/{font_name}', font_size)
    draw = ImageDraw.Draw(img)

    if is_drop_lines.lower() == 'Yes'.lower():
        image_item = random_fall(image_item[1:])

    x = start_x
    initial_y = start_y
    gap = line_gap
    gap_count = 0

    name = str(os.path.splitext(image_name)[0])
    
    for item in image_item:
        draw.text((x, initial_y + gap_count * gap), item, (rgb_r, rgb_g, rgb_b), font=font)
        gap_count = gap_count + 1
        name = name + ', ' + item

    img.save(f'output_folder/image_{count}, {name}.png')


def process_pictures(all_combinations):
    count = 0
    total_combination = len(all_combinations)

    for combinations in all_combinations:
        image_item = []

        for combination in combinations:
            image_item.append(combination)

        count = count + 1
        if count % 1000 == 0:
            print(f'Please wait..... (Processed {count} out of {total_combination} Images)')

        write_in_picture(image_item, count)


def start_process():
    photos_list = list_of_photos(photos_path)
    lines = fetch_all_lines(lines_path)

    if len(lines) > 0:
        possible_combination = len(photos_list)

        for line in lines:
            possible_combination = possible_combination * len(line)
        
        print('\nAll possible combination  =>', possible_combination)
        print('Combination you asked for =>', input_combinations)
        
        process_combination = input_combinations

        if input_combinations == 0:
            process_combination = possible_combination
            print('As 0 making for all possible combination')
        
        if input_combinations > possible_combination:
            process_combination = possible_combination
            print('\nYou are asking more combination than possible. We will process for ', possible_combination, ' combinations')
        
        is_traditional = is_traditional_algorithm(possible_combination, process_combination)
        
        if is_traditional:
            print('\nMaking All Combinations.....')
            all_combination = make_traditional_combination(photos_list, lines, process_combination)
        else:
            print('\nMaking Smart Combinations.....')
            all_combination = make_smart_combination(photos_list, lines, process_combination)
        
        delete_from_local_folder('output_folder/')
        
        print('Started to Make Images.....\nPlease wait.....\n')
        process_pictures(all_combination)

    else:
        print('\nNo lines found!!')


if __name__ == '__main__':
    photos_path = 'input_folder/photos/'
    lines_path = 'input_lines/'
    hyper_param_path = 'hyperParam.txt'

    try:
        print('\nReading Hyper Parameters.....')
        input_combinations, is_drop_lines, font_size, rgb_r, rgb_g, rgb_b, start_x, start_y, line_gap, font_name = read_hyper_parameters(hyper_param_path)
        remove_probs = read_probability_parameters(hyper_param_path)
    except:
        raise Exception('\nCan not Read from Hyper Parameters!!')

    try:
        print('Start Processing.....')
        start_process()
        print('\nFinished Processing all Images!!')
    except:
        raise Exception('\nSome Error occurred!!')
