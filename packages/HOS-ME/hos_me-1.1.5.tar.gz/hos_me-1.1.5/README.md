# HOS ME

一个功能强大的办公自动化平台，支持批量任务处理、模板管理、复杂内容渲染和文档导入导出。

## 功能特性

### 核心功能
- **模板管理**：支持XML模板格式，支持模板导入导出
- **批量处理**：支持批量生成文档、批量转换等功能
- **文档转换**：支持多种格式之间的转换，包括DOCX、PDF、JSON、EXCEL、MD等
- **图片处理**：支持图片自动排序、OCR识别等功能
- **图表渲染**：支持多种图表类型的渲染
- **OCR功能**：集成DeepSeek OCR，支持图片内容识别和模板变量填充

### 扩展功能
- **会议管理**：支持会议纪要生成、会议安排等功能
- **项目管理**：支持项目计划、进度跟踪等功能
- **知识库**：支持知识管理、检索等功能
- **日程管理**：支持日程安排、提醒等功能
- **审批管理**：支持审批流程、状态跟踪等功能
- **任务管理**：支持任务分配、进度跟踪等功能

## 安装方法

### 从PyPI安装

```bash
pip install HOS_ME
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/hos-me/hos-me.git
cd hos-me

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 安装完整版本（包含所有可选依赖）

```bash
pip install HOS_ME[full]
```

## 快速开始

### 命令行使用

```bash
# 查看帮助
hos-me --help

# 初始化配置
hos-me init

# 运行服务器
hos-me run

# 显示版本信息
hos-me version

# 检查状态
hos-me status
```

### 通过配置文件运行

```bash
# 使用指定配置文件运行
hos-me run --config ~/.hos-me/config.json

# 启用调试模式
hos-me run --debug

# 指定主机和端口
hos-me run --host 127.0.0.1 --port 8000
```

### 配置文件

配置文件位于 `~/.hos-me/config.json`，您可以根据需要修改配置：

```json
{
  "api_key": "your_api_key",
  "deepseek_api_key": "your_deepseek_api_key",
  "ollama_url": "http://localhost:11434",
  "log_level": "INFO",
  "port": 5000,
  "host": "0.0.0.0",
  "debug": false,
  "upload_folder": "~/.hos-me/uploads",
  "log_folder": "~/.hos-me/logs"
}
```

### 系统设置文件

系统设置文件位于项目根目录的 `system_settings.json`，包含模板设置、API设置、系统设置和RAG设置：

```json
{
  "template_settings": {
    "output_before": {
      "format": "txt",
      "encoding": "utf-8"
    },
    "output_during": {
      "docx": {
        "font_name": "微软雅黑",
        "font_size": 12,
        "margin": {"top": 2.54, "right": 2.54, "bottom": 2.54, "left": 2.54},
        "line_spacing": 1.5
      }
    }
  },
  "api_settings": {
    "default_api_source": "deepseek",
    "request_timeout": 30,
    "max_retries": 3
  },
  "system_settings": {
    "app_name": "HOS可扩展式办公平台",
    "version": "1.1.3",
    "debug": false
  },
  "rag_settings": {
    "default_library_id": "",
    "auto_generate_embeddings": true,
    "summary_settings": {
      "enabled": true,
      "max_chars": 100,
      "include_filename": true,
      "include_content_preview": true
    }
  }
}
```

## 功能使用

### 文件上传下载

#### 单文件上传

```bash
curl -X POST -F "file=@path/to/file.txt" http://localhost:5000/api/upload
```

#### 多文件上传

```bash
curl -X POST -F "files=@path/to/file1.txt" -F "files=@path/to/file2.txt" http://localhost:5000/api/upload/multiple
```

#### 文件下载

```bash
curl -O http://localhost:5000/api/download/filename.txt
```

### RAG库使用

#### 创建RAG库

```bash
curl -X POST -H "Content-Type: application/json" -d '{"name": "我的RAG库", "description": "测试RAG库"}' http://localhost:5000/api/rag/libraries
```

#### 上传文档到RAG库

```bash
curl -X POST -F "library_id=raglib_1234567890" -F "file=@path/to/document.txt" -F "title=文档标题" http://localhost:5000/api/rag/documents/upload
```

#### 使用RAG库生成报告

```bash
curl -X POST -H "Content-Type: application/json" -d '{"prompt": "生成一份关于AI的报告", "rag_library_id": "raglib_1234567890"}' http://localhost:5000/api/generate_single_report
```

## 配置指南

### 日志配置

日志文件位于 `~/.hos-me/logs/hos-me.log`，可以通过修改配置文件中的 `log_level` 来调整日志级别：

- DEBUG: 详细调试信息
- INFO: 普通信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误信息

### 上传下载配置

- 上传文件保存位置：`~/.hos-me/uploads`
- 支持的文件类型：txt, docx, pdf, xls, xlsx, csv
- 最大文件大小：10MB（可在system_settings.json中修改）

### RAG配置

RAG配置位于 `system_settings.json` 中的 `rag_settings` 部分：

- `enabled_rag`: 是否启用RAG功能
- `default_library_id`: 默认使用的RAG库ID
- `auto_generate_embeddings`: 是否自动生成嵌入
- `summary_settings`: 文档总结配置
  - `enabled`: 是否启用自动总结
  - `max_chars`: 总结的最大字符数
  - `include_filename`: 是否包含文件名
  - `include_content_preview`: 是否包含内容预览

## 常见问题

### 安装后无法运行

确保所有依赖都已正确安装：

```bash
pip install HOS_ME[full]
```

### 上传文件失败

- 检查文件大小是否超过限制
- 检查文件类型是否被支持
- 检查上传目录权限

### RAG功能无法使用

- 确保已安装sentence_transformers依赖
- 确保RAG库已创建并包含文档
- 确保已生成文档嵌入

### 应用无法启动

- 检查配置文件是否正确
- 检查端口是否被占用
- 检查日志文件获取详细错误信息

## API 文档

### 健康检查

```bash
GET /api/health
```

### 文件上传

```bash
# 单文件上传
POST /api/upload
Content-Type: multipart/form-data

# 多文件上传
POST /api/upload/multiple
Content-Type: multipart/form-data
```

### 文件下载

```bash
GET /api/download/<filename>
```

### 模板管理

```bash
# 获取所有模板
GET /api/templates

# 获取指定模板
GET /api/templates/<template_id>

# 创建模板
POST /api/templates

# 更新模板
PUT /api/templates/<template_id>

# 删除模板
DELETE /api/templates/<template_id>
```

## 开发指南

### 安装开发依赖

```bash
pip install HOS_ME[dev]
```

### 运行测试

```bash
pytest
```

### 代码风格检查

```bash
flake8
black .
isort .
```

### 构建文档

```bash
sphinx-build -b html docs/source docs/build
```

## 目录结构

```
HOS_ME/
├── HOS_ME/
│   ├── templates/           # 模板文件
│   ├── static/             # 静态资源
│   ├── utils/              # 工具模块
│   ├── __init__.py         # 包初始化
│   └── app.py             # 主应用
├── templates_storage/      # 模板存储
├── requirements.txt        # 依赖列表
├── setup.py               # 安装配置
└── README.md              # 项目说明
```

## 依赖项

### 核心依赖
- Flask>=2.0.0
- requests>=2.25.0
- python-dotenv>=0.20.0
- python-docx>=1.0.0
- lxml>=4.6.0
- pillow>=8.0.0

### 上传下载功能依赖
- flask-dropzone>=2.0.0
- flask-uploads>=0.2.1

### 命令行界面依赖
- click>=8.0.0

### 日志系统依赖
- python-json-logger>=2.0.0

### 文件处理依赖
- PyPDF2>=2.0.0
- openpyxl>=3.0.7
- pandas>=1.3.0

## 许可证

MIT

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

- 作者：HOS ME Team
- 邮箱：hos_me@example.com
- 项目地址：https://github.com/hos-me/hos-me
