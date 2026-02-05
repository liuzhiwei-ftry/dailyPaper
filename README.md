# dailyPaper - 智能日报生成工具
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 项目简介
`dailyPaper` 是一款基于 PySide6 构建的桌面端智能日报生成工具，集成火山方舟AI能力实现日报内容自动化生成，支持模板自定义、历史数据存储、Excel导出等核心功能，旨在降低人工编写日报的成本，标准化日报输出格式，适配个人/团队日常办公场景。

## 核心技术栈
| 类别         | 技术/工具                                                                 |
|--------------|---------------------------------------------------------------------------|
| 开发语言     | Python 3.8+                                                               |
| 桌面端UI     | PySide6                                                                   |
| AI能力       | 火山方舟AI SDK                                                            |
| 数据存储     | SQLite                                                                    |
| 辅助工具     | 配置管理（config.ini）、Excel导出（openpyxl）、日志管理、Git版本控制       |

## 快速开始
### 1. 环境准备
确保本地已安装 **Python 3.8 及以上版本**（推荐3.9/3.10），未安装的可从[Python官网](https://www.python.org/downloads/)下载安装（安装时勾选「Add Python to PATH」）。

#### 1.1 克隆仓库
```bash
# 替换为实际仓库地址
git clone https://github.com/liuzhiwei-ftry/dailyPaper.git
cd dailyPaper
```

#### 1.2 安装依赖
项目核心依赖已整理至`requirements.txt`（先在项目根目录创建该文件），文件内容如下：
```txt
# requirements.txt
pyside6>=6.5.0
requests>=2.31.0
openpyxl>=3.1.2
python-dotenv>=1.0.0
sqlite3>=2.6.0  # Python内置，无需额外安装
loguru>=0.7.2   # 可选，替代原生logger更友好
```

执行安装命令：
```bash
# 使用pip安装依赖
pip install -r requirements.txt

# 国内用户建议使用镜像源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 配置AI接口
火山方舟AI接口需提前申请密钥（参考[火山方舟官方文档](https://www.volcengine.com/docs/82379/1263279)），配置步骤如下：

#### 2.1 编辑配置文件
打开项目根目录的`config.ini`，替换以下核心配置项：
```ini
[AI_CONFIG]
# 火山方舟API密钥（必填）
api_key = your_volc_ark_api_key
# 火山方舟AI接口端点（以官方文档为准）
api_url = https://ark.cn-beijing.volces.com/api/v3/chat/completions
# AI请求超时时间（单位：秒）
timeout = 30
# AI生成参数（可调整）
temperature = 0.7  # 生成随机性，0-1之间，越小越固定
max_tokens = 1000  # 生成内容最大长度

[DB_CONFIG]
# 日报历史数据库路径（默认本地）
db_path = ./daily_paper.db
# 标识信息数据库路径
identifier_db_path = ./identifier.sqlite

[UI_CONFIG]
# 默认日报模板路径
default_template = ./resources/default_template.txt
# UI窗口大小
window_width = 800
window_height = 600
```

#### 2.2 验证AI配置（可选）
运行AI SDK测试脚本，验证接口连通性：
```bash
python test_sdk.py
```
若输出「AI接口调用成功」则配置正常；若报错，检查`api_key`、`api_url`是否正确，或网络/权限是否受限。

### 3. 初始化数据库
首次运行需初始化SQLite数据表（存储日报历史、模板配置等），执行以下命令：
```bash
python db/db_init.py
```
执行成功后，项目根目录会生成`daily_paper.db`和`identifier.sqlite`文件（请勿手动删除/修改），日志输出如下则代表初始化完成：
```
2024-XX-XX XX:XX:XX - INFO - 数据库连接成功
2024-XX-XX XX:XX:XX - INFO - 日报历史表创建完成
2024-XX-XX XX:XX:XX - INFO - 模板配置表创建完成
2024-XX-XX XX:XX:XX - INFO - 数据库初始化完成
```

### 4. 启动工具
完成以上配置后，直接运行主程序启动桌面端UI：
```bash
# 项目根目录执行
python main.py
```
启动成功后会弹出可视化操作窗口，界面包含以下核心区域：
- 「基础信息」：填写日期、汇报人、所属部门等；
- 「工作内容」：输入今日完成事项、进度、问题等；
- 「模板选择」：选择默认模板/自定义模板；
- 「操作区」：生成日报、预览、导出Excel、查看历史。

### 5. 生成与导出日报
#### 5.1 生成日报
1. 在UI中填写「基础信息」和「工作内容」（必填项标红）；
2. 点击「选择模板」（默认使用`resources/default_template.txt`）；
3. 点击「生成日报」按钮，等待AI处理（约1-3秒）；
4. 生成完成后，「预览区」会展示格式化的日报内容，支持手动编辑。

#### 5.2 导出Excel
1. 预览并确认日报内容无误后，点击「导出Excel」按钮；
2. 选择导出路径（默认保存至`./output/日报_YYYYMMDD_汇报人.xlsx`）；
3. 导出成功后会弹窗提示，可直接打开文件查看。

#### 5.3 查看历史日报
1. 点击UI左侧「历史记录」标签；
2. 可按日期/汇报人筛选历史日报；
3. 选中某条记录，点击「查看」可预览内容，「导出」可重新导出Excel。