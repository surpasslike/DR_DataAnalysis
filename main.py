import pandas as pd
import os

DATA_DIR = 'data'
OUTPUT_FILE = 'data/output.xlsx'


def hex2dec(s):
    return int(str(s), 16)


def mc2df(file):
    return pd.read_csv(file, names=range(50), lineterminator='\n', dtype=str)


df_mc_li = []
combined_dfs = []
mc_name_li = []
last_snsyaw_values = []  # 存储每个GNRMC记录对应的最后一个SNSYAW值
last_snsrawyaw_values = []  # 存储每个GNRMC记录对应的最后一个SNSRAWYAW值

for f in os.scandir(DATA_DIR):
    if f.path.endswith('.mc'):
        df_mc = mc2df(f.path)
        df_mc_li.append(df_mc)
        mc_name_li.append(f.name)

        # 提取 $GNRMC 数据并创建副本来避免 SettingWithCopyWarning
        df_GNRMC = df_mc[df_mc[0] == '$GNRMC'].copy()
        df_GNRMC['last_snsyaw_value'] = pd.NA  # 用 pd.NA 初始化新列

        # 检查是否有GNRMC数据
        if not df_GNRMC.empty:
            # 获取第一行GNRMC的第8列数据，并转换为浮点数
            first_gnrmc_speed = pd.to_numeric(df_GNRMC.iloc[0, 8], errors='coerce')

            df_SNSYAW = df_mc[df_mc[0] == '$SNSYAW'].copy()
            df_SNSYAW = df_SNSYAW.iloc[:, :15]
            df_SNSYAW['can_raw_yaw_rate'] = .0

            # 检查是否有SNSYAW数据并且GNRMC的速度值不是缺失值
            if not df_SNSYAW.empty and first_gnrmc_speed is not None and not pd.isna(first_gnrmc_speed):
                # 将GNRMC的第一行速度值赋给SNSYAW的第一行can_raw_yaw_rate列
                df_SNSYAW.iloc[0, df_SNSYAW.columns.get_loc('can_raw_yaw_rate')] = first_gnrmc_speed

        # 处理 $SNSYAW 数据
        for i in df_SNSYAW.index:
            if i == df_SNSYAW.index[0]: continue
            prev_idx = df_SNSYAW.index[df_SNSYAW.index.get_loc(i) - 1]
            # 这里的代码已经为df_SNSYAW计算了can_raw_yaw_rate
            df_SNSYAW.loc[i, 'can_raw_yaw_rate'] = (-0.1 * round(
                float(df_SNSYAW.loc[i, 2]) if float(df_SNSYAW.loc[i, 2]) < 2000 else float(
                    df_SNSYAW.loc[i, 2]) - 6553.6, 1)) + df_SNSYAW.loc[prev_idx, 'can_raw_yaw_rate']

        # 提取 $SNSRAWYAW 数据并创建副本来避免 SettingWithCopyWarning
        df_SNSRAWYAW = df_mc[df_mc[0] == '$SNSRAWYAW'].copy()
        df_GNRMC['last_snsrawyaw_values'] = pd.NA  # 用 pd.NA 初始化新列

        # 检查是否有GNRMC数据
        if not df_GNRMC.empty:
            # 获取第一行GNRMC的第8列数据，并转换为浮点数
            first_gnrmc_speed = pd.to_numeric(df_GNRMC.iloc[0, 8], errors='coerce')

            df_SNSRAWYAW = df_mc[df_mc[0] == '$SNSRAWYAW'].copy()
            df_SNSRAWYAW = df_SNSRAWYAW.iloc[:, :16]
            df_SNSRAWYAW['sns_raw_yaw_rate'] = .000

            # 检查是否有SNSYAW数据并且GNRMC的速度值不是缺失值
            if not df_SNSRAWYAW.empty and first_gnrmc_speed is not None and not pd.isna(first_gnrmc_speed):
                # 将GNRMC的第一行速度值赋给SNSYAW的第一行sns_raw_yaw_rate列
                df_SNSRAWYAW.iloc[0, df_SNSRAWYAW.columns.get_loc('sns_raw_yaw_rate')] = first_gnrmc_speed

        # 处理 $SNSYAW 数据
        for i in df_SNSRAWYAW.index:
            if i == df_SNSRAWYAW.index[0]: continue
            prev_idx = df_SNSRAWYAW.index[df_SNSRAWYAW.index.get_loc(i) - 1]

            # TODO:求平均数

            # 这里的代码已经为df_SNSRAWYAW计算了sns_raw_yaw_rate
            df_SNSRAWYAW.loc[i, 'sns_raw_yaw_rate'] = (-0.10 * (round(
                float(df_SNSRAWYAW.loc[i, 2]) if float(df_SNSRAWYAW.loc[i, 2]) < 2000 else float(
                    df_SNSRAWYAW.loc[i, 2]) - 6553.60, 5) + round(
                float(df_SNSRAWYAW.loc[i, 4]) if float(df_SNSRAWYAW.loc[i, 4]) < 2000 else float(
                    df_SNSRAWYAW.loc[i, 4]) - 6553.60, 5) + round(
                float(df_SNSRAWYAW.loc[i, 6]) if float(df_SNSRAWYAW.loc[i, 6]) < 2000 else float(
                    df_SNSRAWYAW.loc[i, 6]) - 6553.60, 5) + round(
                float(df_SNSRAWYAW.loc[i, 8]) if float(df_SNSRAWYAW.loc[i, 8]) < 2000 else float(
                    df_SNSRAWYAW.loc[i, 8]) - 6553.60, 5) + round(
                float(df_SNSRAWYAW.loc[i, 10]) if float(df_SNSRAWYAW.loc[i, 10]) < 2000 else float(
                    df_SNSRAWYAW.loc[i, 10]) - 6553.60, 5)) / 5) + df_SNSRAWYAW.loc[prev_idx, 'sns_raw_yaw_rate']

        # 初始化用于存储最后一个SNSYAW值和can_raw_yaw_rate的变量
        last_snsyaw_value = pd.NA
        last_can_raw_yaw_rate = None  # 新增变量

        # 初始化一个列表来存储所有的can_raw_yaw_rate值
        all_raw_yaw_rates = []

        # 初始化用于存储最后一个SNSYAW值和sns_raw_yaw_rate的变量
        last_snsrawyaw_values = pd.NA
        last_sns_raw_yaw_rate = None  # 新增变量

        # 初始化一个列表来存储所有的sns_raw_yaw_rate值
        all_sns_raw_yaw_rates = []

        # 遍历 df_mc 提取 can_raw_yaw_rate 并在需要时计算平均值
        for index, row in df_mc.iterrows():
            if row[0] == '$SNSYAW':
                # 获取当前的can_raw_yaw_rate值，并转换为浮点数
                current_can_raw_yaw_rate = float(df_SNSYAW.loc[df_SNSYAW.index == index, 'can_raw_yaw_rate'].values[0])

                # 将当前值添加到列表中
                all_raw_yaw_rates.append(current_can_raw_yaw_rate)

            # elif row[0] == '$SNSRAWYAW':
            #     # 获取当前的can_raw_yaw_rate值，并转换为浮点数
            #     current_sns_raw_yaw_rate = float(
            #         df_SNSRAWYAW.loc[df_SNSRAWYAW.index == index, 'sns_raw_yaw_rate'].values[0])

            # # 将当前值添加到列表中
            # all_sns_raw_yaw_rates.append(current_sns_raw_yaw_rate)

            elif row[0] == '$GNRMC':
                # 如果有记录的can_raw_yaw_rate值，计算它们的平均值
                if all_raw_yaw_rates:
                    last_snsyaw_value = sum(all_raw_yaw_rates) / len(all_raw_yaw_rates)
                    df_GNRMC.loc[index, 'can_raw_yaw_rate'] = last_snsyaw_value
                else:
                    last_snsyaw_value = None  # 如果没有值，设置为None

                # 为$GNRMC行设置平均的last_snsyaw_value
                df_GNRMC.loc[index, 'last_snsyaw_value'] = last_snsyaw_value

                # 重置all_raw_yaw_rates列表以便为下一个$GNRMC条目收集新的can_raw_yaw_rate值
                all_raw_yaw_rates = []

        # 按照原顺序合并数据
        combined = pd.concat([df_SNSYAW, df_SNSRAWYAW, df_GNRMC], axis=0).sort_index()
        combined_dfs.append(combined)

        # 添加整个SNSYAW的最后值列表
        sns_yaw_values = df_GNRMC['last_snsyaw_value'].tolist()

        last_snsyaw_values.append(sns_yaw_values)

writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')

for i, combined_df in enumerate(combined_dfs):
    combined_df.to_excel(writer, sheet_name=mc_name_li[i], index=False)

workbook = writer.book
charts_sheet = workbook.add_worksheet('charts')

# 创建图表
for i, combined_df in enumerate(combined_dfs):
    gnrmc_data = combined_df[combined_df[0] == '$GNRMC']
    sns_yaw_data = combined_df[combined_df[0] == '$SNSYAW']

    # 将时间和速度数据转换为数值格式
    gnrmc_data.loc[:, 1] = gnrmc_data.loc[:, 1].apply(float)
    gnrmc_data.loc[:, 8] = gnrmc_data.loc[:, 8].astype(float)
    gnrmc_data = gnrmc_data.reset_index(drop=True)
    time_data = gnrmc_data[1].reset_index(drop=True)
    speed_data = gnrmc_data[8].reset_index(drop=True)

    # 把时间和速度数据写入Excel的Charts工作表
    charts_sheet.write('A1', 'Time')
    charts_sheet.write('B1', 'GPS')
    charts_sheet.write('C1', 'YAW')

    for j in range(len(time_data)):
        last_snsyaw = last_snsyaw_values[i][j] if not pd.isna(last_snsyaw_values[i][j]) else None
        charts_sheet.write(j + 1, 0, time_data.iloc[j])  # 时间写入A列
        charts_sheet.write(j + 1, 1, speed_data.iloc[j])  # 速度写入B列
        charts_sheet.write(j + 1, 2, last_snsyaw)  # 最后的SNSYAW值写入C列

    # 创建图表
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name': f'GPS',
        'categories': f'=charts!$A$2:$A${len(time_data) + 1}',
        'values': f'=charts!$B$2:$B${len(speed_data) + 1}',
        'line': {'color': 'blue'},
        'y_axis': 0,  # 将此系列设置到第一个Y轴（默认值）
    })

    # 添加第C列的数据作为新的系列（SNSYAW值）
    chart.add_series({
        'name': f'YAW',
        'categories': f'=charts!$A$2:$A${len(time_data) + 1}',  # 使用相同的X轴数据
        'values': f'=charts!$C$2:$C${len(time_data) + 1}',  # 这里假设时间数据和SNSYAW数据行数相同
        'line': {'color': 'red'},  # 使用不同的颜色以区分线条
        'y_axis': 0,  # 将此系列设置到第一个Y轴
    })

    # 设置图表的标题和轴标签等
    chart.set_title({'name': f'{mc_name_li[i]} Comparison'})
    chart.set_x_axis({'name': 'Time'})
    chart.set_y_axis({'name': 'Angle'})

    # 将图表插入到 charts_sheet 中的指定位置
    charts_sheet.insert_chart(f'D{i * 20 + 1}', chart)
writer._save()
