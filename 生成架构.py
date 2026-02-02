import os
import re

class ProjectStructureGenerator:
    def __init__(self, arch_file_path: str = "项目目录架构.txt"):
        self.arch_file_path = arch_file_path
        self.level_map = {}  # 存储每个层级对应的完整父路径

    def parse_and_create(self):
        if not os.path.exists(self.arch_file_path):
            print(f"❌ 错误：架构文件 {self.arch_file_path} 不存在")
            return

        with open(self.arch_file_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f if line.strip() and not line.strip().startswith("#")]

        for line in lines:
            # 1. 彻底剥离所有树形符号（├──、└──、│）和注释
            clean_line = re.sub(r"^(├──|└──|│\s*|\s*)+", "", line).split("#")[0].strip()
            if not clean_line:
                continue

            # 2. 计算当前行的层级（按前导空格/符号的宽度计算）
            level = 0
            for c in line:
                if c in (" ", "│", "├", "└"):
                    level += 1
                else:
                    break
            level = level // 4  # 按4空格为一个层级单位

            # 3. 获取父路径
            if level == 0:
                parent = os.getcwd()
            else:
                parent = self.level_map.get(level - 1, os.getcwd())

            # 4. 处理节点（文件夹/文件）
            node = clean_line
            full_path = os.path.join(parent, node.rstrip("/"))

            if node.endswith("/"):
                # 创建文件夹
                os.makedirs(full_path, exist_ok=True)
                self.level_map[level] = full_path
                print(f"✅ 文件夹：{full_path}")
            else:
                # 创建空文件
                if not os.path.exists(full_path):
                    with open(full_path, "x", encoding="utf-8"):
                        print(f"✅ 文件：{full_path}")
                else:
                    print(f"ℹ️ 文件已存在：{full_path}")

if __name__ == "__main__":
    generator = ProjectStructureGenerator()
    generator.parse_and_create()