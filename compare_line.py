import difflib
import os

# 比较data文件夹的两个文件中,文本有哪一行仅在自身内部存在

def read_file_cleaned(file_path):
    """读取文件，移除空白行和注释，返回清理后的行列表。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        cleaned_lines = []
        for line in lines:
            stripped_line = line.strip()
            # 移除空行
            if not stripped_line:
                continue
            # 移除单行注释（假设XML文件不包含常见的代码注释）
            cleaned_lines.append(stripped_line)
        return cleaned_lines

def compare_files(file1_path, file2_path):
    file1_lines = set(read_file_cleaned(file1_path))
    file2_lines = set(read_file_cleaned(file2_path))

    diff1 = file1_lines.difference(file2_lines)
    diff2 = file2_lines.difference(file1_lines)

    if not diff1 and not diff2:
        print("两个文件内容相同。")
    else:
        if diff1:
            print(f"仅在{os.path.basename(file1_path)}中存在的行：")
            for line in diff1:
                print(line)
        if diff2:
            print(f"仅在{os.path.basename(file2_path)}中存在的行：")
            for line in diff2:
                print(line)

if __name__ == "__main__":
    data_dir = 'data'
    files = os.listdir(data_dir)
    if len(files) < 2:
        print("需要至少两个文件才能进行比较。")
    else:
        file1 = os.path.join(data_dir, files[0])
        file2 = os.path.join(data_dir, files[1])
        compare_files(file1, file2)
