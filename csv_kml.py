import pandas as pd
import xml.etree.ElementTree as ET
import re
import json


# 载入 CSV 文件
csv_file = 'SH20231025_0134_0227CSV_0215_0216进入新建路隧道.csv'
# 设置 low_memory 参数为 False
df = pd.read_csv(csv_file, header=None, low_memory=False)

# 创建 KML 文件的根
kml_root = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
document = ET.SubElement(kml_root, 'Document')

# 解析数据并添加到 KML 文件
for index, row in df.iterrows():
    # 寻找包含 "enhancedPosition" 的行
    if isinstance(row[12], str) and 'enhancedPosition' in row[12]:
        # 使用正则表达式提取 JSON 字符串
        match = re.search(r'\{.*\}', row[12])
        if match:
            json_data = match.group(0)
            data = json.loads(json_data)

            # 创建 Placemark
            placemark = ET.SubElement(document, 'Placemark')
            point = ET.SubElement(placemark, 'Point')
            coordinates = ET.SubElement(point, 'coordinates')
            coordinates.text = f"{data['enhancedPosition']['lon']},{data['enhancedPosition']['lat']},0"

# 生成 KML 文件
tree = ET.ElementTree(kml_root)
tree.write('CSVSH20231025_0134_0227CSV_0215_0216进入新建路隧道.kml')

print("KML file generated as 'output.kml'")