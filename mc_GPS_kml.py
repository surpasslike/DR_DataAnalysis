from xml.dom.minidom import Document
import os


# 将度和度分格式转换为小数格式
def convert_to_decimal_rmc(coord, direction):
    degrees = float(coord[:2]) if direction in ['N', 'S'] else float(coord[:3])
    minutes = float(coord[2:]) if direction in ['N', 'S'] else float(coord[3:])
    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


# 解析GPS数据，获取纬度和经度
def parse_gps_data(data):
    gps_data = []
    for line in data.splitlines():
        parts = line.split(',')
        try:
            if line.startswith("$GNRMC,"):
                # 这是GPS,纬度和经度在第 3 和第 5 个部分
                lat = convert_to_decimal_rmc(parts[3], parts[4])
                lon = convert_to_decimal_rmc(parts[5], parts[6])
                gps_data.append((lat, lon))
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
