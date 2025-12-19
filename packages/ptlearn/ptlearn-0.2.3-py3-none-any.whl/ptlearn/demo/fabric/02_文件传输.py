"""
Fabric 文件传输
===============
使用 Fabric 进行文件上传和下载操作
支持单文件传输，目录传输需要配合其他方法

核心方法：
- put(): 上传本地文件到远程
- get(): 下载远程文件到本地
"""

from fabric import Connection
from pathlib import Path

# region 示例1: 上传文件 (put)
if False:  # 改为 True 可运行此示例
    with Connection("user@hostname") as conn:
        # 基本上传：本地文件 -> 远程路径
        conn.put("local_file.txt", "/remote/path/file.txt")
        
        # 上传到远程目录（保持原文件名）
        conn.put("local_file.txt", "/remote/path/")
        
        # 使用 Path 对象
        local_path = Path("./data/config.json")
        conn.put(local_path, "/etc/app/config.json")
        
        # put() 返回 Result 对象，包含传输信息
        result = conn.put("app.py", "/home/user/")
        print(f"本地路径: {result.local}")
        print(f"远程路径: {result.remote}")
# endregion

# region 示例2: 下载文件 (get)
if False:  # 改为 True 可运行此示例
    with Connection("user@hostname") as conn:
        # 基本下载：远程文件 -> 本地路径
        conn.get("/remote/path/file.txt", "local_file.txt")
        
        # 下载到本地目录（保持原文件名）
        conn.get("/var/log/app.log", "./logs/")
        
        # 使用 Path 对象
        local_path = Path("./backup")
        conn.get("/etc/nginx/nginx.conf", local_path / "nginx.conf")
        
        # get() 同样返回 Result 对象
        result = conn.get("/home/user/data.csv", "./")
        print(f"远程路径: {result.remote}")
        print(f"本地路径: {result.local}")
# endregion

# region 示例3: 传输目录（使用 tar 打包）
if False:  # 改为 True 可运行此示例
    with Connection("user@hostname") as conn:
        # Fabric 不直接支持目录传输，需要先打包
        
        # 上传目录：先本地打包，上传，再远程解压
        from invoke import run as local_run
        
        # 本地打包
        local_run("tar -czf project.tar.gz ./project/", hide=True)
        # 上传
        conn.put("project.tar.gz", "/home/user/")
        # 远程解压
        conn.run("cd /home/user && tar -xzf project.tar.gz", hide=True)
        # 清理
        conn.run("rm /home/user/project.tar.gz", hide=True)
        local_run("rm project.tar.gz", hide=True)
        
        print("目录上传完成")
        
        # 下载目录：远程打包，下载，本地解压
        conn.run("cd /home/user && tar -czf backup.tar.gz ./data/", hide=True)
        conn.get("/home/user/backup.tar.gz", "./")
        local_run("tar -xzf backup.tar.gz", hide=True)
        conn.run("rm /home/user/backup.tar.gz", hide=True)
        local_run("rm backup.tar.gz", hide=True)
        
        print("目录下载完成")
# endregion

# region 示例4: 文件权限和所有者
if False:  # 改为 True 可运行此示例
    with Connection("user@hostname") as conn:
        # 上传后修改权限
        conn.put("script.sh", "/home/user/script.sh")
        conn.run("chmod +x /home/user/script.sh")
        
        # 上传后修改所有者（需要 sudo 权限）
        conn.put("config.conf", "/tmp/config.conf")
        conn.run("sudo mv /tmp/config.conf /etc/app/")
        conn.run("sudo chown root:root /etc/app/config.conf")
        conn.run("sudo chmod 644 /etc/app/config.conf")
        
        print("文件权限设置完成")
# endregion

# region 示例5: 模拟演示
if True:  # 改为 False 可跳过此示例
    print("=" * 50)
    print("Fabric 文件传输演示（模拟）")
    print("=" * 50)
    
    print("\n1. 上传文件 put()：")
    print('   conn.put("local.txt", "/remote/path/file.txt")')
    print('   conn.put("local.txt", "/remote/dir/")  # 保持文件名')
    print('   result = conn.put(...)  # 返回 Result 对象')
    
    print("\n2. 下载文件 get()：")
    print('   conn.get("/remote/file.txt", "local.txt")')
    print('   conn.get("/remote/file.txt", "./local_dir/")')
    
    print("\n3. 目录传输（需要打包）：")
    print("   上传: 本地 tar -> put -> 远程 untar")
    print("   下载: 远程 tar -> get -> 本地 untar")
    
    print("\n4. Result 对象属性：")
    print("   result.local  - 本地路径")
    print("   result.remote - 远程路径")
    
    print("\n5. 常见模式：")
    print('   conn.put("app.py", "/home/user/")')
    print('   conn.run("chmod +x /home/user/app.py")')
# endregion
