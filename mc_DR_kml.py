from xml.dom.minidom import Document

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

    return  mon, day + 1, hour+1, minute, second, millisecond

# 解析GPS数据，获取纬度和经度
def parse_gps_data(data):
    gps_data = []
    for line in data.splitlines():
        parts = line.split(',')
        try:
            if line.startswith("$PKTHEAD,"):
                lon = float(parts[4])
                lat = float(parts[5])
                extra_data = int(parts[-1])  # 获取最后一个元素作为时间戳
                timestamp = transform_from_timestamp(extra_data)  # 将时间戳转换为实际日期时间
                gps_data.append((lat, lon, timestamp))
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

        # 创建description元素
        description = doc.createElement('description')
        description_text = doc.createTextNode(str(point[2]))  # point[2] 是转换后的日期时间
        description.appendChild(description_text)
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

# 文件名
mc_file_name = "GPS20231122133052TEXT.mc"

# 读取.mc文件
with open(mc_file_name, 'r') as file:
    mc_file_data = file.read()

# 使用 parse_gps_data 解析GPS数据
gps_points = parse_gps_data(mc_file_data)

# 使用 create_kml 生成KML内容
kml_content = create_kml(gps_points)

# 输出KML内容到控制台或保存到文件
print(kml_content)
# 可选：将KML内容保存到文件
with open("DR_go_GPS20231122133052TEXT.kml", "w") as kml_file:
    kml_file.write(kml_content)
