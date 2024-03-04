import difflib
import sys

def remove_inline_comments(line):
    # 对于C++和Java的单行注释
    pos = line.find("//")
    if pos != -1:
        return line[:pos] + "\n"  # 保留注释之前的内容，添加换行符
    # 对于Python的单行注释
    pos = line.find("#")
    if pos != -1:
        return line[:pos] + "\n"  # 保留注释之前的内容，添加换行符
    return line  # 没有找到注释，返回原始行

def read_file_ignore_comments_and_blank_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        processed_lines = []
        in_block_comment = False
        for line in lines:
            # 移除行首和行尾的空白字符
            stripped_line = line.strip()
            if not stripped_line:
                continue  # 忽略空行
            # 处理多行注释的开始
            if "/*" in stripped_line:
                in_block_comment = True
                line = stripped_line.split("/*")[0] + "\n"
            # 处理多行注释的结束
            if "*/" in stripped_line:
                in_block_comment = False
                line = stripped_line.split("*/")[-1] + "\n"
                if not line.strip():
                    continue
            if in_block_comment or not line.strip():
                continue  # 忽略多行注释内的行和空行
            line = remove_inline_comments(line)  # 移除行内注释
            if line.strip():  # 检查移除注释后的行是否为空
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
    if len(sys.argv) == 3:
        compare_files(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python compare.py <file1> <file2>")
