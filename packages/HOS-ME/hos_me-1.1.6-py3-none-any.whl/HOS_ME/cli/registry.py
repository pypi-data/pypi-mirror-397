#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令注册表，用于管理和自动发现命令
"""

import importlib
import os
import sys
from types import ModuleType

class CommandRegistry:
    """命令注册表，用于管理和自动发现命令"""
    
    def __init__(self):
        self.commands = []
        self.modules = []
    
    def register(self, command_class):
        """注册命令类"""
        if command_class not in self.commands:
            self.commands.append(command_class)
    
    def get_commands(self):
        """获取所有注册的命令"""
        return self.commands
    
    def discover_commands(self, package_name="HOS_ME.commands"):
        """自动发现命令"""
        try:
            # 导入命令包
            package = importlib.import_module(package_name)
            # 获取包路径
            package_path = package.__path__[0]
            # 遍历包中的所有文件
            for file_name in os.listdir(package_path):
                if file_name.endswith(".py") and file_name != "__init__.py":
                    # 导入模块
                    module_name = f"{package_name}.{file_name[:-3]}"
                    module = importlib.import_module(module_name)
                    self.modules.append(module)
                    # 查找并注册所有BaseCommand子类
                    for name, obj in module.__dict__.items():
                        if isinstance(obj, type) and obj.__name__ != "BaseCommand":
                            try:
                                from .base import BaseCommand
                                if issubclass(obj, BaseCommand):
                                    self.register(obj)
                            except (ImportError, TypeError):
                                continue
        except ImportError:
            # 命令包不存在，跳过
            pass
    
    def register_all(self, cli):
        """注册所有命令到CLI"""
        for command_class in self.commands:
            command_class.register(cli)
    
    def add_module_commands(self, module):
        """添加模块中的命令"""
        # 查找并注册所有BaseCommand子类
        from .base import BaseCommand
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and obj.__name__ != "BaseCommand":
                try:
                    if issubclass(obj, BaseCommand):
                        self.register(obj)
                except (ImportError, TypeError):
                    continue
    
    def get_command(self, name, group=""):
        """根据名称获取命令"""
        for command_class in self.commands:
            if command_class.name == name and command_class.group == group:
                return command_class
        return None
