import os
import shutil
# 自动将每个文件夹内与其同名的子文件夹中的所有内容移动到该文件夹中，并删除空的同名子文件夹。
#
# 文件夹名字“A”->文件夹名字“A”->文件内容
# ----------->
# 文件夹名字“A”->文件内容
#
# 脚本使用方法：把move_contents.py位于第一层“文件夹名字“A””同级目录下，cmd下运行"python move_contents.py"即可
def move_contents_up():
    # 获取脚本所在的当前工作目录
    root_dir = os.getcwd()
    # 遍历root_dir下的所有项目
    for entry in os.listdir(root_dir):
        entry_path = os.path.join(root_dir, entry)
        # 确保这是一个文件夹
        if os.path.isdir(entry_path):
            # 检查是否存在同名的子文件夹
            inner_folder_path = os.path.join(entry_path, entry)
            if os.path.isdir(inner_folder_path):
                # 遍历同名子文件夹内的所有内容
                for content in os.listdir(inner_folder_path):
                    content_path = os.path.join(inner_folder_path, content)
                    # 将内容移动到顶级文件夹
                    shutil.move(content_path, entry_path)
                # 删除现在空的同名子文件夹
                os.rmdir(inner_folder_path)

# 执行函数
move_contents_up()
