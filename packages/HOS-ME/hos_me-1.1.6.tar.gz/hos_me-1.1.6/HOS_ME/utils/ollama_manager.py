import os
import sys
import requests
import subprocess
import platform
import logging
import time
from typing import Dict, List, Optional, Tuple

class OllamaManager:
    """Ollama管理器，负责Ollama的安装、管理和模型下载"""
    
    def __init__(self, config: Dict):
        """初始化Ollama管理器"""
        self.config = config
        self.logger = logging.getLogger('hos-me')
        self.base_url = config.get('ollama', {}).get('base_url', 'http://localhost:11434')
        
    def check_ollama_installed(self) -> bool:
        """检查Ollama是否已安装"""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Ollama已安装: {result.stdout.strip()}")
                return True
            self.logger.info("Ollama未安装")
            return False
        except FileNotFoundError:
            self.logger.info("Ollama未安装")
            return False
        except Exception as e:
            self.logger.error(f"检查Ollama安装状态失败: {str(e)}")
            return False
    
    def download_ollama(self) -> bool:
        """下载并安装Ollama"""
        try:
            self.logger.info("开始下载Ollama...")
            
            # 根据操作系统选择安装命令
            os_type = platform.system().lower()
            
            if os_type == 'windows':
                # Windows安装命令
                install_cmd = 'powershell -Command "iwr -useb https://ollama.com/install.ps1 | iex"'
                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            elif os_type == 'darwin':
                # macOS安装命令
                install_cmd = '/bin/bash -c "$(curl -fsSL https://ollama.com/install.sh)"'
                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            elif os_type == 'linux':
                # Linux安装命令
                install_cmd = '/bin/bash -c "$(curl -fsSL https://ollama.com/install.sh)"'
                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            else:
                self.logger.error(f"不支持的操作系统: {os_type}")
                return False
            
            if result.returncode == 0:
                self.logger.info("Ollama安装成功")
                return True
            else:
                self.logger.error(f"Ollama安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"下载Ollama失败: {str(e)}")
            return False
    
    def start_ollama_service(self) -> bool:
        """启动Ollama服务"""
        try:
            self.logger.info("启动Ollama服务...")
            
            os_type = platform.system().lower()
            
            if os_type == 'windows':
                # Windows启动Ollama服务
                result = subprocess.run(['ollama', 'serve'], 
                                       shell=True, 
                                       capture_output=True, 
                                       text=True, 
                                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            elif os_type in ['darwin', 'linux']:
                # macOS和Linux启动Ollama服务
                result = subprocess.run(['ollama', 'serve'], 
                                       shell=True, 
                                       capture_output=True, 
                                       text=True, 
                                       start_new_session=True)
            else:
                self.logger.error(f"不支持的操作系统: {os_type}")
                return False
            
            # 等待服务启动
            time.sleep(5)
            
            # 检查服务是否正常运行
            if self.check_ollama_running():
                self.logger.info("Ollama服务启动成功")
                return True
            else:
                self.logger.error("Ollama服务启动失败")
                return False
                
        except Exception as e:
            self.logger.error(f"启动Ollama服务失败: {str(e)}")
            return False
    
    def check_ollama_running(self) -> bool:
        """检查Ollama服务是否正在运行"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[Dict]:
        """列出已安装的模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取模型列表失败: {str(e)}")
            return []
    
    def download_model(self, model_name: str, callback=None) -> Tuple[bool, str]:
        """下载指定模型"""
        try:
            self.logger.info(f"开始下载模型: {model_name}")
            
            # 检查Ollama是否正在运行
            if not self.check_ollama_running():
                self.logger.info("Ollama服务未运行，尝试启动...")
                if not self.start_ollama_service():
                    return False, "Ollama服务启动失败"
            
            # 构建请求数据
            data = {
                "name": model_name,
                "stream": True
            }
            
            # 发送请求下载模型
            response = requests.post(f"{self.base_url}/api/pull", 
                                    json=data, 
                                    stream=True, 
                                    timeout=self.config.get('timeout', 300))
            
            if response.status_code == 200:
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        # 解析JSON响应
                        import json
                        try:
                            line_data = json.loads(line.decode('utf-8'))
                            if 'status' in line_data:
                                status = line_data['status']
                                self.logger.info(f"模型下载状态: {status}")
                                if callback:
                                    callback(status)
                            if 'error' in line_data:
                                error = line_data['error']
                                self.logger.error(f"模型下载失败: {error}")
                                return False, error
                        except json.JSONDecodeError:
                            continue
                
                self.logger.info(f"模型下载成功: {model_name}")
                return True, f"模型下载成功: {model_name}"
            else:
                error_msg = f"模型下载失败，HTTP状态码: {response.status_code}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            error_msg = f"模型下载失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"模型下载失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_model(self, model_name: str) -> bool:
        """删除指定模型"""
        try:
            self.logger.info(f"删除模型: {model_name}")
            
            data = {
                "name": model_name
            }
            
            response = requests.delete(f"{self.base_url}/api/delete", 
                                     json=data, 
                                     timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"模型删除成功: {model_name}")
                return True
            else:
                self.logger.error(f"模型删除失败: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"删除模型失败: {str(e)}")
            return False
    
    def check_model_installed(self, model_name: str) -> bool:
        """检查指定模型是否已安装"""
        models = self.list_models()
        for model in models:
            if model['name'].startswith(model_name):
                return True
        return False
    
    def get_recommended_models(self) -> List[Dict]:
        """获取推荐模型列表"""
        return self.config.get('recommended_models', [])
    
    def install_default_model(self) -> bool:
        """安装默认模型"""
        default_model = self.config.get('default_model', 'a3b-q8_0')
        self.logger.info(f"安装默认模型: {default_model}")
        return self.download_model(default_model)[0]
    
    def setup_ollama(self) -> bool:
        """完整设置Ollama，包括安装、启动服务和下载默认模型"""
        try:
            # 检查Ollama是否已安装
            if not self.check_ollama_installed():
                # 下载并安装Ollama
                if not self.download_ollama():
                    return False
            
            # 检查Ollama服务是否正在运行
            if not self.check_ollama_running():
                # 启动Ollama服务
                if not self.start_ollama_service():
                    return False
            
            # 检查默认模型是否已安装
            default_model = self.config.get('default_model', 'a3b-q8_0')
            if not self.check_model_installed(default_model):
                # 下载默认模型
                if not self.download_model(default_model)[0]:
                    return False
            
            self.logger.info("Ollama设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"设置Ollama失败: {str(e)}")
            return False
