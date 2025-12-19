#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOS ME命令行工具初始化
"""

from .registry import CommandRegistry
from .base import BaseCommand

# 创建全局命令注册表
command_registry = CommandRegistry()

# 导出主要类
__all__ = ['command_registry', 'BaseCommand']
