#!/bin/bash
## 构建rayel-rpa-executor包，并发布到 PyPI，后续RPA项目使用此包


# 确保脚本在错误时退出
set -e

# 进入对应环境
source .venv/bin/activate

# 自动递增版本号
echo "正在递增版本号..."
python << 'EOF'
import re

# 读取 pyproject.toml
with open('pyproject.toml', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找版本号（三段式）
version_pattern = r'version = "(\d+)\.(\d+)\.(\d+)"'
match = re.search(version_pattern, content)

if match:
    # 解析版本号
    major, minor, patch = map(int, match.groups())
    # 递增补丁版本号
    patch += 1
    old_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    new_version = f"{major}.{minor}.{patch}"
    
    # 替换版本号
    new_content = content.replace(
        f'version = "{old_version}"',
        f'version = "{new_version}"'
    )
    
    # 写回文件
    with open('pyproject.toml', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"版本号已更新: {old_version} -> {new_version}")
else:
    print("错误: 未找到版本号")
    exit(1)
EOF

# 检查 Python 脚本是否执行成功
if [ $? -ne 0 ]; then
    echo "版本号更新失败"
    exit 1
fi

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
uv pip install build
python -m build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "构建失败：dist 目录不存在"
    exit 1
fi

# 上传到 PyPI
echo "正在上传到 PyPI..."
uv pip install twine
python -m twine upload dist/*

echo "发布完成！" 