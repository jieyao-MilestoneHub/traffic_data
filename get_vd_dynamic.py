# import requests
# import xml.etree.ElementTree as ET
# import pandas as pd


# # 指定 URL
# url = 'https://tisvcloud.freeway.gov.tw/history/motc20/VDLive.xml'

# # 使用 requests 獲取 XML 數據
# response = requests.get(url)

# root = ET.fromstring(response.text)

# data = {}

# def extract_elements(element):
#     for child in element:
#         if child.text.strip():
#             if child.tag not in data:
#                 data[child.tag] = [child.text.strip()]
#             else:
#                 data[child.tag].append(child.text.strip())
#         extract_elements(child)

# extract_elements(root)

# for tag, value in data.items():
#     print(f"{tag}: {len(value)}")


import requests
import datetime
import os
from gzip import GzipFile
from io import BytesIO

# 设置基础 URL 和日期
base_url = "https://tisvcloud.freeway.gov.tw"
date = datetime.date.today().strftime('%Y%m%d')  # 例如 '20240430'

# 创建保存数据的目录
if not os.path.exists(date):
    os.makedirs(date)

# 遍历一天中的每一分钟
for hour in range(24):
    for minute in range(60):
        time_str = f"{hour:02d}{minute:02d}"
        file_url = f"{base_url}/history/motc20/VD/{date}/VDLive_{time_str}.xml.gz"
        
        # 发起请求
        response = requests.get(file_url)
        if response.status_code == 200:
            # 解压数据
            with GzipFile(fileobj=BytesIO(response.content)) as gz:
                xml_content = gz.read()
                
            # 保存解压后的 XML 文件
            with open(f"{date}/VDLive_{time_str}.xml", 'wb') as xml_file:
                xml_file.write(xml_content)
                
            print(f"Downloaded and saved VDLive_{time_str}.xml")
        else:
            print(f"Failed to download file for {time_str}")

# 注：运行此脚本前确保网络连接稳定，考虑到数据量可能很大和下载时间较长。
