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


# 时间戳转换为日期时间的函数
def transform_from_timestamp(timestamp):
    day_sum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    mil_of_day = 24 * 3600 * 1000
    mil_of_hour = 3600 * 1000
    timestamp_backup = timestamp

    # 时间戳溢出处理
    if timestamp > 315537897599999:
        timestamp = 315537897599999

    low, high = 1, 9999
    while low <= high:
        mid = (low + high) // 2
        t = ((mid - 1) * 365 + (mid - 1) // 4 - (mid - 1) // 100 + (mid - 1) // 400) * mil_of_day
        if t == timestamp:
            low = mid + 1
            break
        elif t < timestamp:
            low = mid + 1
        else:
            high = mid - 1
    year = low - 1

    timestamp -= ((year - 1) * 365 + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400) * mil_of_day
    is_leap_year = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

    for mon in range(1, 13):
        if (day_sum[mon] + (1 if is_leap_year and mon > 2 else 0)) * mil_of_day > timestamp:
            break
    timestamp -= day_sum[mon - 1] * mil_of_day

    day = timestamp // mil_of_day
    timestamp -= day * mil_of_day
    hour = timestamp // mil_of_hour
    timestamp -= hour * mil_of_hour
    minute = timestamp // 60000
    timestamp -= minute * 60000
    second = timestamp // 1000
    millisecond = timestamp % 1000

    return hour + 1, minute, second, millisecond, timestamp_backup


# 解析GPS数据，获取纬度、经度、时间、$GNACCURACY和$GNGST的信息
def parse_gps_data(data):
    gps_data = []
    accuracy = None
    gngst_info = None

    for line in data.splitlines():
        parts = line.split(',')
        try:
            if line.startswith("$PKTHEAD,"):
                lon = float(parts[4])
                lat = float(parts[5])
                extra_data = int(parts[11])  # 获取最后一个元素作为时间戳
                timestamp = transform_from_timestamp(extra_data)  # 将时间戳转换为实际日期时间
                gps_data.append((lat, lon, timestamp, accuracy, gngst_info))
            elif line.startswith("$GNACCURACY,"):
                # 提取$GNACCURACY的信息
                accuracy_parts = line.split(',')
                accuracy = f'{accuracy_parts[1]},{accuracy_parts[2]}'  # 提取第一个和第二个数字
            elif line.startswith("$GNGST,"):
                # 提取$GNGST的信息
                gngst_parts = line.split(',')
                gngst_info = f'{gngst_parts[2]},{gngst_parts[3]},{gngst_parts[4]}'  # 提取第二、第三和第四个数字
        except (IndexError, ValueError):
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

        # 添加时间信息、$GNACCURACY信息和$GNGST信息到description
        description = doc.createElement('description')
        description_text = f'Time: {point[2]}, Accuracy: {point[3]}, GNGST: {point[4]}'  # 使用提取的信息
        description.appendChild(doc.createTextNode(description_text))
        placemark.appendChild(description)

        # 创建名称（name）元素
        name = doc.createElement('name')
        second = point[2][2]  # 获取秒
        name_text = doc.createTextNode(f'Second: {second}, Accuracy:{point[3]}, GNGST: {point[4]}')  # 显示秒、$GNACCURACY信息和$GNGST信息
        name.appendChild(name_text)
        placemark.appendChild(name)

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
        kml_file_name = f"DR_Accuracy_{mc_file_name[:-3]}.kml"
        kml_file_path = os.path.join(kml_folder, kml_file_name)

        # 使用 create_kml 生成KML内容
        kml_content = create_kml(gps_points)

        # 将KML内容保存到文件
        with open(kml_file_path, "w") as kml_file:
            kml_file.write(kml_content)

        print(f"Generated KML file: {kml_file_path}")
