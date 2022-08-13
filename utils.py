import os
import csv

def csv_pipeline(item:dict, title:str, header:list[str]):
    base_dir = '结果文件' + os.sep + title
    file_path = base_dir + os.sep + title + '.csv'

    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
    if not os.path.isfile(file_path):
        is_first_write = 1
    else:
        is_first_write = 0
        
    if item:
        with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if is_first_write:
                if header:
                    writer.writerow(header)
            writer.writerow([item[key] for key in item.keys()])