import time
import os
import re
import requests
import js2py  # 导入 js2py
import json
import pymysql
from enum import Enum
from typing import Optional
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field

class DpipblockTools(str, Enum):
    PORT_ADD = "port_add"
    PORT_DELETE = "port_delete"

def convert_time_to_seconds(time_str: str) -> str:
    time_str = time_str.strip().lower()
    
    if time_str in ["永久", "permanent", "forever", "-1"]:
        return "-1"
    
    if time_str.isdigit():
        return time_str
    
    match = re.match(r'(\d+)\s*([a-zA-Z\u4e00-\u9fff]+)', time_str)
    if not match:
        return "180"
    
    number = int(match.group(1))
    unit = match.group(2)
    
    time_units = {
        '分钟': 60, 'min': 60, 'm': 60, 'minute': 60, 'minutes': 60,
        '小时': 3600, 'hour': 3600, 'hours': 3600, 'h': 3600,
        '天': 86400, 'day': 86400, 'days': 86400, 'd': 86400,
        '周': 604800, 'week': 604800, 'weeks': 604800, 'w': 604800,
        '月': 2592000, 'month': 2592000, 'months': 2592000,
        '年': 31536000, 'year': 31536000, 'years': 31536000, 'y': 31536000,
        '秒': 1, 'second': 1, 'seconds': 1, 's': 1, 'sec': 1,
    }
    
    multiplier = time_units.get(unit, 1)
    return str(number * multiplier)


# 数据库操作
class DB():
    # 在setting.databases我已创建了数据库链接相关信息，在下方调用时直接写语句即可
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='abc123456', db='wuhu_data'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd)
        # 创建游标
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()


# 查询数据
def select_data(select_sql):
    with DB() as db:
        db.execute(select_sql)
        data_list = db.fetchall()
        return data_list


def get_account(sys_name):
    sql = "select * from ai_account where sys_name = '" + sys_name + "'"
    sys_account = select_data(sql)
    return sys_account[0]


def dpfhq_login(username: str, password: str) -> Optional[dict]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(current_dir, "7_dpfhq.js")
    
    with open(js_file_path, "r", encoding="UTF-8") as file:
        js_code = file.read()
    
    ctx = js2py.EvalJs()
    ctx.execute(js_code)

    headers1 = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "10.138.36.249:8890",
        "Referer": "https://10.138.36.249:8890/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-API-Language": "zh_CN",
        "X-API-Version": "5.5R10",
        "X-FROM-UI": "1",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }
    url1 = "https://10.138.36.249:8890/rest/before_login"
    main_url_html1 = requests.get(url=url1, headers=headers1, verify=False)
    response1 = main_url_html1.text
    json_result1 = json.loads(response1)
    result1 = json_result1['result'][0]
    uuid = result1['uuid']

    headers2 = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "10.138.36.249:8890",
        "Referer": "https://10.138.36.249:8890/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-API-Language": "zh_CN",
        "X-API-Version": "5.5R10",
        "X-Auth-Uuid": uuid,
        "X-FROM-UI": "1",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }
    url2 = "https://10.138.36.249:8890/rest/pub-key"
    main_url_html2 = requests.get(url=url2, headers=headers2, verify=False)
    response2 = main_url_html2.text
    json_result2 = json.loads(response2)
    result2 = json_result2['result'][0]
    long_public_key = result2['long_public_key']
    public_key = result2['public_key']

    uname = ctx.call("encrypt", username, public_key, long_public_key)
    pwd = ctx.call("encrypt", password, public_key, long_public_key)

    params = {"username": uname, "password": pwd}
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "205",
        "Content-Type": "text/plain;charset=UTF-8",
        "Host": "10.138.36.249:8890",
        "Origin": "https://10.138.36.249:8890",
        "Referer": "https://10.138.36.249:8890/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-API-Language": "zh_CN",
        "X-API-Version": "5.5R10",
        "X-Auth-Uuid": uuid,
        "X-FROM-UI": "1",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }
    url = 'https://10.138.36.249:8890/rest/login'
    main_url_html = requests.post(url=url, json=params, headers=headers, verify=False)
    response = main_url_html.text
    json_result = json.loads(response)
    result = json_result['result'][0]

    cj_headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "https_2819643222001444=" + result['token'],
        "Host": "10.138.36.249:8890",
        "Referer": "https://10.138.36.249:8890/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "X-API-Language": "zh_CN",
        "X-API-Version": "5.5R10",
        "X-Active-Module": "homepage",
        "X-Auth-Fromrootvsys": "true",
        "X-Auth-Role": "admin",
        "X-Auth-Token": result['token'],
        "X-Auth-Username": "pczhang",
        "X-Auth-VsysId": "0",
        "X-FROM-UI": "1",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": 'Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }
    return cj_headers

def dpfhq_logout(headers):
    url = 'https://10.138.36.249:8890/rest/logout'
    main_url_html = requests.delete(url=url, headers=headers, verify=False)


class DpipblockServer:
    def dpfhq_port_management_add(self, ip: str, time_str: str) -> str:
        account = get_account('迪普防火墙')
        headers = dpfhq_login(account['sys_account'], account['sys_password'])
        if headers is not None:
            time_seconds = convert_time_to_seconds(time_str)
            params = [{"vr":"trust-vr","is_ipv6":0,"ip_str":ip,"is_group":"0","server_name":"","age":time_seconds}]
            url = 'https://10.138.36.249:8890/rest/behavior_blockIp'
            main_url_html = requests.post(url=url, json=params, headers=headers, verify=False)
            response = main_url_html.text
            json_result = json.loads(response)
            dpfhq_logout(headers)
            if json_result['success']:
                return "("+ip+")端口封禁成功！"
            else:
                return "("+ip+")端口封禁失败！"
    
    def dpfhq_port_management_delete(self, ip: str) -> str:
        account = get_account('迪普防火墙')
        headers = dpfhq_login(account['sys_account'], account['sys_password'])
        if headers is not None:
            params = {"keys":[{"ip_str":ip,"is_user":0,"vr":"trust-vr","is_group":0}]}
            url = 'https://10.138.36.249:8890/rest/behavior_blockIp'
            main_url_html = requests.delete(url=url, json=params, headers=headers, verify=False)
            response = main_url_html.text
            json_result = json.loads(response)
            dpfhq_logout(headers)
            if json_result['success']:
                return "(" + ip + ")端口解禁成功！"
            else:
                return "(" + ip + ")端口解禁失败！"

async def serve() -> None:
    server = Server("mcp-dpipblock")
    tdpipblock_server = DpipblockServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=DpipblockTools.PORT_ADD.value,
                description="在防火墙层面封禁IP地址",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be blocked at the port level, e.g., '192.168.1.1'",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time of sequestration. Supports formats: '永久'(permanent), '1分钟'/'1min'/'1m', '1小时'/'1hour'/'1h', '1天'/'1day'/'1d', '1周'/'1week'/'1w', '1月'/'1month', '1年'/'1year'/'1y', or pure number (seconds)",
                        }
                    },
                    "required": ["ip", "time"]
                },
            ),
            Tool(
                name=DpipblockTools.PORT_DELETE.value,
                description="在防火墙层面解封IP地址",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be unblocked at the port level, e.g., '192.168.1.1'",
                        }
                    },
                    "required": ["ip"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                case DpipblockTools.PORT_ADD.value:
                    if not all(k in arguments for k in ["ip", "time"]):
                        raise ValueError("Missing required arguments")
                    result = tdpipblock_server.dpfhq_port_management_add(arguments["ip"], arguments["time"])

                case DpipblockTools.PORT_DELETE.value:
                    ip = arguments.get("ip")
                    if not ip:
                        raise ValueError("Missing required argument: ip")
                    result = tdpipblock_server.dpfhq_port_management_delete(ip)

                case _:
                    raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            raise ValueError(f"Error processing mcp-server-dpipblock query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)