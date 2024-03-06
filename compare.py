import difflib
import sys
import os


# 模仿gitk来比较代码不同,但是我自动忽略了所有注释
# 把两个代码文件放入data文件夹中即可

def remove_inline_comments(line):
    pos = line.find("//")
    if pos != -1:
        return line[:pos] + "\n"
    pos = line.find("#")
    if pos != -1:
        return line[:pos] + "\n"
    return line


def read_file_ignore_comments_and_blank_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        processed_lines = []
        in_block_comment = False
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if "/*" in stripped_line:
                in_block_comment = True
                line = stripped_line.split("/*")[0] + "\n"
            if "*/" in stripped_line:
                in_block_comment = False
                line = stripped_line.split("*/")[-1] + "\n"
                if not line.strip():
                    continue
            if in_block_comment or not line.strip():
                continue
            line = remove_inline_comments(line)
            if line.strip():
                processed_lines.append(line)
        return processed_lines


def compare_files(file1_path, file2_path):
    file1_lines = read_file_ignore_comments_and_blank_lines(file1_path)
    file2_lines = read_file_ignore_comments_and_blank_lines(file2_path)

    diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path)

    differences = list(diff)
    if not differences:
        print("两个文件没有差异。")
    else:
        print("文件差异：")
        sys.stdout.writelines(differences)


if __name__ == "__main__":
    data_dir = 'data'
    files = os.listdir(data_dir)
    if len(files) < 2:
        print("需要至少两个文件才能进行比较。")
    else:
        file1 = os.path.join(data_dir, files[0])
        file2 = os.path.join(data_dir, files[1])
        compare_files(file1, file2)
