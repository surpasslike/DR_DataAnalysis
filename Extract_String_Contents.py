import re
import os

# 把<string name="app_name">Benutzerhandbuch</string>提取为Benutzerhandbuch
def extract_string_contents(file_path):
    # 用于存储提取出的字符串
    extracted_strings = []

    try:
        # 打开文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # 使用正则表达式找出所有的<string>标签内容
            matches = re.findall(r'<string name="[^"]+">([^<]+)</string>', content)
            extracted_strings.extend(matches)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return extracted_strings


def save_results(results, output_path):
    # 保存提取结果到新文件
    with open(output_path, 'w', encoding='utf-8') as file:
        for line in results:
            file.write(line + '\n')


def main():
    data_folder = "data"
    # 列出data文件夹中所有的.txt文件
    for file_name in os.listdir(data_folder):
        if file_name.endswith('.txt'):
            input_path = os.path.join(data_folder, file_name)

            # 提取字符串
            results = extract_string_contents(input_path)
            if results is not None:
                # 构建输出文件的路径
                output_file_name = os.path.splitext(file_name)[0] + "output.txt"
                output_path = os.path.join(data_folder, output_file_name)

                # 保存结果
                save_results(results, output_path)
                print(f"Results have been saved to {output_path}")


if __name__ == '__main__':
    main()
