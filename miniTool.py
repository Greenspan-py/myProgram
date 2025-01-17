import json
import tkinter as tk
import sys
import os

import requests
from bs4 import BeautifulSoup

# 总体请求函数
def request(content, temp_file_name):

    # 从html中截取数据
    def extract_data_from_html():

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(resp.content, 'html.parser')

        # 存储结果的字典
        data = {}

        dl_classes = ['dataItem01', 'dataItem02', 'dataItem03']

        fund_name = soup.find('span', class_='fix_fname').get_text(strip=True)
        fund_code = soup.find('span', class_='fix_fcode').get_text(strip=True)

        data['基金名称'] = fund_name
        data['基金代码'] = fund_code
        data['变化率'] = []
        data['数值变化'] = []

        for dl_class in dl_classes:
            dl_tag = soup.find('dl', class_=dl_class)
            if dl_tag:
                # 查找所有 dt 标签
                dt_tag = dl_tag.find('dt')
                if dt_tag:
                    span = dt_tag.find('span', class_='sp01')
                else:
                    span = '-'
                # 查找所有 dd 标签
                dd_tags = dl_tag.find_all('dd')

                for dd_tag in dd_tags:
                    # 判断 dd 标签是否有 class
                    if 'class' in dd_tag.attrs:
                        # 有 class 的 dd 标签
                        span_tags = dd_tag.find_all('span')
                        span_contents = [span.get_text(strip=True) for span in span_tags if span.get_text(strip=True)]
                        data_elem = {
                            span.get_text(strip=True): span_contents
                        }
                        data['数值变化'].append(data_elem)
                    else:
                        # 无 class 的 dd 标签
                        span_tags = dd_tag.find_all('span')
                        span_contents = [span.get_text(strip=True) for span in span_tags if span.get_text(strip=True)]
                        data['变化率'].append(span_contents)
        return json.dumps(data, ensure_ascii=False, indent=4)

    url = f'https://fund.eastmoney.com/{content}.html?spm=search'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    resp = requests.get(url, headers=headers)

    json_data = extract_data_from_html()

    # 将解析后的内容写入文件
    with open(temp_file_name, 'w', encoding='utf-8') as f:
        f.write(json_data)

def on_button_click():
    try:
        money_code = entry.get()

        # 获取当前工作目录
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()
        temp_file_path = os.path.join(base_path, 'temp_file.txt')

        # 创建一个临时文件路径
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            temp_file.write('NULL')  # 如果需要，可以在这里写入初始数据

        request(money_code, temp_file_path)

        # 读取临时文件中的内容并显示在文本区域
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            data = temp_file.read()
            text_area.delete('1.0', tk.END)  # 清除旧内容
            text_area.insert(tk.END, data)  # 插入新内容

        #可选：删除临时文件
        os.remove(temp_file_path)
    except Exception as e:
        text_area.delete('1.0', tk.END)
        text_area.insert(tk.END, f"错误: {e}")

app = tk.Tk()
app.title("目标基金增长幅度")

label = tk.Label(app, text="请输入基金代码：")
label.pack()

entry = tk.Entry(app)
entry.pack()

button = tk.Button(app, text="查询", command=on_button_click)
button.pack()

# 添加一个文本区域来显示数据
text_area = tk.Text(app)
text_area.pack()

app.mainloop()
