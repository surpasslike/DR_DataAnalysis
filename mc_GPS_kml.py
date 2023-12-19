from xml.dom.minidom import Document
from datetime import datetime, timedelta
import os


# 将度和度分格式转换为小数格式
def convert_to_decimal_rmc(coord, direction):
    degrees = float(coord[:2]) if direction in ['N', 'S'] else float(coord[:3])
    minutes = float(coord[2:]) if direction in ['N', 'S'] else float(coord[3:])
    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


# 解析GPS数据，获取纬度、经度、时间以及$GNACCURACY的信息
def parse_gps_data(data):
    gps_data = []
    accuracy = None

    for line in data.splitlines():
        parts = line.split(',')
        try:
            if line.startswith("$GNRMC,"):
                # 这是GPS,纬度、经度和时间在不同部分
                lat = convert_to_decimal_rmc(parts[3], parts[4])
                lon = convert_to_decimal_rmc(parts[5], parts[6])
                time = parts[1]
                # 解析时间并增加一个小时
                time = datetime.strptime(time, "%H%M%S.%f")
                time += timedelta(hours=1)
                time_str = time.strftime("%H:%M:%S")  # 修改时间格式
                gps_data.append((lat, lon, time_str, accuracy))
            # elif line.startswith("$GNACCURACY,"):
            #     # 提取$GNACCURACY的信息
            #     accuracy_parts = line.split(',')
            #     accuracy = f'{accuracy_parts[1]},{accuracy_parts[2]}'  # 提取第一个和第二个数字
        except (IndexError, ValueError):
            # 跳过错误的行
            continue
    return gps_data


# 生成KML文件
def create_kml(gps_points):
    doc = Document()

    # 创建KML根元素
    kml = doc.createElement('kml')
    kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    doc.appendChild(kml)

    # 创建Document元素
    document = doc.createElement('Document')
    kml.appendChild(document)

    for point in gps_points:
        # 创建Placemark元素
        placemark = doc.createElement('Placemark')
        document.appendChild(placemark)

        # 添加时间信息到description
        description = doc.createElement('description')
        # description_text = f'Time: {point[2]}, Accuracy: {point[3]}'  # 使用提取的时间信息和$GNACCURACY信息
        description_text = f'Time: {point[2]}'  # 使用提取的时间信息
        description.appendChild(doc.createTextNode(description_text))
        placemark.appendChild(description)

        # 创建Point元素
        point_element = doc.createElement('Point')
        placemark.appendChild(point_element)

        # 创建coordinates元素
        coordinates = doc.createElement('coordinates')
        coordinates_text = doc.createTextNode(f'{point[1]},{point[0]},0')
        coordinates.appendChild(coordinates_text)
        point_element.appendChild(coordinates)

    return doc.toprettyxml(indent="  ")


# 处理多个.mc文件
mc_folder = "data"  # 存放.mc文件的文件夹
kml_folder = "data"  # 存放.kml文件的文件夹

for mc_file_name in os.listdir(mc_folder):
    if mc_file_name.endswith(".mc"):
        mc_file_path = os.path.join(mc_folder, mc_file_name)

        # 读取.mc文件
        with open(mc_file_path, 'r') as file:
            mc_file_data = file.read()

        # 使用 parse_gps_data 解析GPS数据
        gps_points = parse_gps_data(mc_file_data)

        # 生成对应的.kml文件名
        kml_file_name = f"GPS_{mc_file_name[:-3]}.kml"
        kml_file_path = os.path.join(kml_folder, kml_file_name)

        # 使用 create_kml 生成KML内容
        kml_content = create_kml(gps_points)

        # 将KML内容保存到文件
        with open(kml_file_path, "w") as kml_file:
            kml_file.write(kml_content)

        print(f"Generated KML file: {kml_file_path}")
