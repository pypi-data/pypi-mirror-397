#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOS ME 主入口文件
用于直接运行HOS_ME模块
"""

import sys
import json
import os
from HOS_ME.app import app, cli

if __name__ == "__main__":
    # 运行命令行工具
    cli()
