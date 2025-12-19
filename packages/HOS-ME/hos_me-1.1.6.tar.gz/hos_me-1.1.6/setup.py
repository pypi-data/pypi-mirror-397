from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import shutil
import json
from pathlib import Path

# Read the requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# Read the README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

class PostInstallCommand(install):
    """Post-installation command to create configuration file and setup environment."""
    def run(self):
        """Run the post-installation command."""
        # 先运行父类的run方法
        install.run(self)
        # Create configuration directory
        config_dir = os.path.expanduser('~/.hos-me')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['uploads', 'reports', 'templates', 'temp', 'logs']
        for subdir in subdirs:
            dir_path = os.path.join(config_dir, subdir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        
        # Create default configuration file
        default_config = {
            'api_key': '',
            'deepseek_api_key': '',
            'ollama_url': 'http://localhost:11434',
            'log_level': 'INFO',
            'port': 5000,
            'host': '0.0.0.0',
            'debug': False,
            'upload_folder': os.path.join(config_dir, 'uploads'),
            'log_folder': os.path.join(config_dir, 'logs'),
            'reports_dir': os.path.join(config_dir, 'reports'),
            'templates_dir': os.path.join(config_dir, 'templates'),
            'temp_dir': os.path.join(config_dir, 'temp')
        }
        
        config_path = os.path.join(config_dir, 'config.json')
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"Configuration file created at: {config_path}")
            print("You can edit this file to configure HOS ME settings.")
        else:
            print(f"Configuration file already exists at: {config_path}")
        
        # Create system_settings.json if it doesn't exist
        system_settings_path = os.path.join(config_dir, 'system_settings.json')
        if not os.path.exists(system_settings_path):
            default_system_settings = {
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
                        },
                        "pdf": {
                            "page_size": "A4",
                            "orientation": "portrait"
                        },
                        "excel": {
                            "sheet_name": "周报"
                        }
                    },
                    "output_after": {
                        "default_save_location": "reports",
                        "naming_rule": "{date}_{user}_{type}.{format}",
                        "auto_save": True
                    }
                },
                "api_settings": {
                    "default_api_source": "deepseek",
                    "request_timeout": 30,
                    "max_retries": 3
                },
                "system_settings": {
                    "app_name": "HOS可扩展式办公平台",
                    "version": "1.1.6",
                    "debug": False,
                    "max_file_size": 10485760,
                    "supported_file_types": ["txt", "docx", "pdf", "xls", "xlsx", "csv"]
                },
                "rag_settings": {
                    "default_library_id": "",
                    "auto_generate_embeddings": True,
                    "default_embedding_model": "all-MiniLM-L6-v2",
                    "similarity_threshold": 0.7,
                    "max_results": 5,
                    "enable_rag": True,
                    "default_visibility": "private",
                    "supported_embedding_models": ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-MiniLM-L6-v2"],
                    "summary_settings": {
                        "enabled": True,
                        "max_chars": 100,
                        "include_filename": True,
                        "include_content_preview": True
                    }
                }
            }
            with open(system_settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_system_settings, f, ensure_ascii=False, indent=2)
            print(f"System settings file created at: {system_settings_path}")
        else:
            print(f"System settings file already exists at: {system_settings_path}")
        
        # Create hos_config.json if it doesn't exist
        hos_config_path = os.path.join(config_dir, 'hos_config.json')
        if not os.path.exists(hos_config_path):
            default_hos_config = {
                "workflows": [],
                "custom_modules": []
            }
            with open(hos_config_path, 'w', encoding='utf-8') as f:
                json.dump(default_hos_config, f, ensure_ascii=False, indent=2)
            print(f"HOS configuration file created at: {hos_config_path}")
        else:
            print(f"HOS configuration file already exists at: {hos_config_path}")



setup(
    name='HOS_ME',
    version='1.1.6',
    author='HOS ME Team',
    author_email='hos_me@example.com',
    description='HOS ME - 一个功能强大的办公自动化平台，支持批量任务处理、模板管理、复杂内容渲染和文档导入导出',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hos-me/hos-me',
    packages=find_packages(include=['HOS_ME', 'HOS_ME.*']),
    include_package_data=True,
    package_data={
        'HOS_ME': [
            'templates/*',
            'static/css/*',
            'static/js/*',
            'workflow_templates.json'
        ],
    },
    data_files=[
        ('config', ['HOS_ME/templates/index.html']),
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0',
            'flake8>=4.0',
            'black>=22.0',
            'isort>=5.0',
            'sphinx>=4.0',
            'sphinx_rtd_theme>=1.0',
        ],
        'full': [
            'PyPDF2>=2.0.0',
            'openpyxl>=3.0.7',
            'pandas>=1.3.0',
            'redis>=4.0.0',
            'celery>=5.0.0',
            'python-daemon>=2.3.0',
            'click>=8.0.0',
            'python-json-logger>=2.0.0',
        ],
        'logging': [
            'python-json-logger>=2.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'hos-me=HOS_ME.app:cli',
            'hosme=HOS_ME.app:cli',
        ],
    },
    zip_safe=False,
    cmdclass={
        'install': PostInstallCommand,
    },
    setup_requires=['wheel'],
    license='MIT',  # 使用SPDX许可证表达式
)
