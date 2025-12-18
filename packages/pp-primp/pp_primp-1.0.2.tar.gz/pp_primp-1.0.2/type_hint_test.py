"""
测试类型提示是否正常工作

在 IDE 中打开这个文件，输入 `client.get(` 应该能看到所有参数的自动补全提示
"""
import pp_primp

# 创建客户端
client = pp_primp.Client(impersonate="chrome_143")

# 当你输入 client.get( 时，IDE 应该显示所有可用的参数：
# - url (必需)
# - params
# - headers
# - cookies
# - auth
# - auth_bearer
# - timeout
# - read_timeout
# - proxy
# - impersonate
# - impersonate_os
# - verify
# - ca_cert_file
# - follow_redirects
# - max_redirects
# - https_only
# - http2_only

# 示例：尝试输入 client.get(url="...", 然后按 Ctrl+Space 应该显示所有参数
response = client.get(
    url="https://httpbin.org/get",
    timeout=10,
    proxy="http://127.0.0.1:8080",
    impersonate="firefox_143",
    https_only=True,
)

print(f"Status: {response.status_code}")

# 同样适用于 post 等其他方法
response2 = client.post(
    url="https://httpbin.org/post",
    json={"key": "value"},
    timeout=10,
    impersonate="safari_18",
    http2_only=True,
)

print(f"Status: {response2.status_code}")
