#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行基础类
"""

import click
from abc import ABC, abstractmethod

class BaseCommand(ABC):
    """所有命令的基类"""
    
    # 命令名称
    name = ""
    # 命令帮助信息
    help = ""
    # 命令组名称（可选）
    group = ""
    # 命令组帮助信息（可选）
    group_help = ""
    # 命令参数配置
    params = []
    
    @abstractmethod
    def run(self, **kwargs):
        """执行命令"""
        pass
    
    @classmethod
    def register(cls, cli):
        """注册命令到CLI"""
        if cls.group:
            # 如果有命令组，创建或获取命令组
            group = getattr(cli, f"{cls.group}_group", None)
            if not group:
                group = click.group(name=cls.group, help=cls.group_help)(lambda: None)
                setattr(cli, f"{cls.group}_group", group)
            # 注册命令到命令组
            command = click.command(name=cls.name, help=cls.help)(cls._execute)
            # 添加参数
            for param in cls.params:
                command = param(command)
            group.add_command(command)
        else:
            # 直接注册命令
            command = click.command(name=cls.name, help=cls.help)(cls._execute)
            # 添加参数
            for param in cls.params:
                command = param(command)
            cli.add_command(command)
    
    @classmethod
    def _execute(cls, **kwargs):
        """命令执行包装器"""
        instance = cls()
        return instance.run(**kwargs)
