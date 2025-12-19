#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具，用于统一管理所有文件的存储和访问
"""

import os
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger('hos-me')

class FileManager:
    """文件管理器类，用于统一管理文件的存储和访问"""
    
    def __init__(self, config):
        """初始化文件管理器"""
        self.config = config
        self.base_dir = os.path.expanduser('~/.hos-me')
        
        # 定义文件存储目录结构
        self.directories = {
            'uploads': os.path.join(self.base_dir, 'uploads'),
            'reports': os.path.join(self.base_dir, 'reports'),
            'templates': os.path.join(self.base_dir, 'templates'),
            'temp': os.path.join(self.base_dir, 'temp'),
            'logs': os.path.join(self.base_dir, 'logs')
        }
        
        # 确保所有目录存在
        self._ensure_directories()
        
        # 初始化文件元数据存储
        self.metadata_file = os.path.join(self.base_dir, 'file_metadata.json')
        self._load_metadata()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        for dir_path in self.directories.values():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"创建目录: {dir_path}")
    
    def _load_metadata(self):
        """加载文件元数据"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"加载文件元数据失败: {str(e)}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """保存文件元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存文件元数据失败: {str(e)}")
    
    def get_file_path(self, file_type, filename):
        """获取文件路径"""
        if file_type not in self.directories:
            raise ValueError(f"不支持的文件类型: {file_type}")
        return os.path.join(self.directories[file_type], filename)
    
    def save_file(self, file_type, filename, content):
        """保存文件"""
        file_path = self.get_file_path(file_type, filename)
        
        try:
            with open(file_path, 'wb' if isinstance(content, bytes) else 'w', encoding='utf-8' if not isinstance(content, bytes) else None) as f:
                f.write(content)
            
            # 更新元数据
            file_key = f"{file_type}/{filename}"
            self.metadata[file_key] = {
                'file_type': file_type,
                'filename': filename,
                'file_path': file_path,
                'size': os.path.getsize(file_path),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self._save_metadata()
            
            logger.info(f"文件保存成功: {file_key}")
            return file_key
        except Exception as e:
            logger.error(f"文件保存失败: {file_type}/{filename}, 错误: {str(e)}")
            raise
    
    def read_file(self, file_type, filename):
        """读取文件内容"""
        file_path = self.get_file_path(file_type, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_type}/{filename}")
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"文件读取失败: {file_type}/{filename}, 错误: {str(e)}")
            raise
    
    def delete_file(self, file_type, filename):
        """删除文件"""
        file_path = self.get_file_path(file_type, filename)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            
            # 更新元数据
            file_key = f"{file_type}/{filename}"
            if file_key in self.metadata:
                del self.metadata[file_key]
                self._save_metadata()
            
            logger.info(f"文件删除成功: {file_type}/{filename}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {file_type}/{filename}, 错误: {str(e)}")
            return False
    
    def get_file_info(self, file_type, filename):
        """获取文件信息"""
        file_key = f"{file_type}/{filename}"
        if file_key in self.metadata:
            return self.metadata[file_key]
        
        # 如果元数据中没有，尝试从文件系统获取
        file_path = self.get_file_path(file_type, filename)
        if os.path.exists(file_path):
            file_info = {
                'file_type': file_type,
                'filename': filename,
                'file_path': file_path,
                'size': os.path.getsize(file_path),
                'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            }
            self.metadata[file_key] = file_info
            self._save_metadata()
            return file_info
        
        return None
    
    def list_files(self, file_type=None):
        """列出文件"""
        if file_type:
            # 列出指定类型的文件
            if file_type not in self.directories:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            dir_path = self.directories[file_type]
            files = []
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    file_info = self.get_file_info(file_type, filename)
                    if file_info:
                        files.append(file_info)
            return files
        else:
            # 列出所有文件
            all_files = []
            for file_type in self.directories:
                all_files.extend(self.list_files(file_type))
            return all_files
    
    def get_file_by_key(self, file_key):
        """根据文件键获取文件信息"""
        if file_key in self.metadata:
            return self.metadata[file_key]
        return None
    
    def exists(self, file_type, filename):
        """检查文件是否存在"""
        file_path = self.get_file_path(file_type, filename)
        return os.path.exists(file_path)
    
    def get_file_size(self, file_type, filename):
        """获取文件大小"""
        file_path = self.get_file_path(file_type, filename)
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path)
    
    def get_relative_path(self, file_type, filename):
        """获取文件相对路径"""
        return f"{file_type}/{filename}"
    
    def resolve_file_path(self, file_key):
        """根据文件键解析文件路径"""
        if '/' in file_key:
            file_type, filename = file_key.split('/', 1)
            return self.get_file_path(file_type, filename)
        # 如果没有斜杠，尝试作为报告文件
        return self.get_file_path('reports', file_key)
    
    def clean_temp_files(self, days=7):
        """清理临时文件"""
        temp_dir = self.directories['temp']
        now = time.time()
        cutoff = now - (days * 86400)  # 86400秒 = 1天
        
        deleted_count = 0
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"清理临时文件: {filename}")
                    except Exception as e:
                        logger.error(f"清理临时文件失败: {filename}, 错误: {str(e)}")
        
        logger.info(f"共清理 {deleted_count} 个临时文件")
        return deleted_count