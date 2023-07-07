import os

folder_path = "pdf_txt"  # 指定文件夹路径
total_word_count = 0  # 初始化总字数为0

for filename in os.listdir(folder_path):  # 遍历文件夹中的所有文件
    if filename.endswith(".txt"):  # 判断文件是否为txt文件
        file_path = os.path.join(folder_path, filename)  # 获取文件路径
        with open(file_path, "r", encoding="utf-8") as f:  # 打开文件
            content = f.read()  # 读取文件内容
            word_count = len(content)  # 统计文件字数
            total_word_count += word_count  # 将文件字数加入总字数

print("所有txt文件的总字数为：", total_word_count)