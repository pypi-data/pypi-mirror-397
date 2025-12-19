#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.ollama_manager import OllamaManager
from HOS_ME.utils.report_generator import Config

class OllamaStatusCommand(BaseCommand):
    """检查Ollama状态命令"""
    
    name = "status"
    help = "检查Ollama安装和运行状态"
    group = "ollama"
    group_help = "Ollama管理相关命令"
    
    def run(self):
        """执行检查Ollama状态命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        is_installed = ollama_manager.check_ollama_installed()
        is_running = ollama_manager.check_ollama_running()
        installed_models = ollama_manager.list_models()
        recommended_models = ollama_manager.get_recommended_models()
        
        click.echo(f"Ollama安装状态: {'已安装' if is_installed else '未安装'}")
        click.echo(f"Ollama运行状态: {'运行中' if is_running else '未运行'}")
        
        click.echo("\n已安装模型:")
        for model in installed_models:
            click.echo(f"- {model['name']} (大小: {model['size']}，修改时间: {model['modified_at']})")
        
        click.echo("\n推荐模型:")
        for model in recommended_models:
            click.echo(f"- {model['name']}: {model['description']} {'(默认)' if model.get('default') else ''}")
        
        return {
            "is_installed": is_installed,
            "is_running": is_running,
            "installed_models": installed_models,
            "recommended_models": recommended_models
        }

class OllamaInstallCommand(BaseCommand):
    """安装Ollama命令"""
    
    name = "install"
    help = "下载并安装Ollama"
    group = "ollama"
    
    def run(self):
        """执行安装Ollama命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        if ollama_manager.check_ollama_installed():
            click.echo("Ollama已安装，无需再次安装")
            return True
        
        click.echo("开始安装Ollama...")
        success = ollama_manager.download_ollama()
        
        if success:
            click.echo("Ollama安装成功")
        else:
            click.echo("Ollama安装失败", err=True)
        
        return success

class OllamaStartCommand(BaseCommand):
    """启动Ollama服务命令"""
    
    name = "start"
    help = "启动Ollama服务"
    group = "ollama"
    
    def run(self):
        """执行启动Ollama服务命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        if ollama_manager.check_ollama_running():
            click.echo("Ollama服务已在运行")
            return True
        
        click.echo("开始启动Ollama服务...")
        success = ollama_manager.start_ollama_service()
        
        if success:
            click.echo("Ollama服务启动成功")
        else:
            click.echo("Ollama服务启动失败", err=True)
        
        return success

class OllamaDownloadModelCommand(BaseCommand):
    """下载Ollama模型命令"""
    
    name = "download-model"
    help = "下载Ollama模型"
    group = "ollama"
    
    params = [
        click.option('--model-name', '-m', required=True, help='模型名称'),
    ]
    
    def run(self, model_name):
        """执行下载Ollama模型命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        click.echo(f"开始下载模型: {model_name}...")
        
        def callback(status):
            click.echo(f"  {status}")
        
        success, message = ollama_manager.download_model(model_name, callback)
        
        if success:
            click.echo(f"模型下载成功: {model_name}")
        else:
            click.echo(f"模型下载失败: {message}", err=True)
        
        return success

class OllamaDeleteModelCommand(BaseCommand):
    """删除Ollama模型命令"""
    
    name = "delete-model"
    help = "删除Ollama模型"
    group = "ollama"
    
    params = [
        click.option('--model-name', '-m', required=True, help='模型名称'),
    ]
    
    def run(self, model_name):
        """执行删除Ollama模型命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        click.echo(f"开始删除模型: {model_name}...")
        success = ollama_manager.delete_model(model_name)
        
        if success:
            click.echo(f"模型删除成功: {model_name}")
        else:
            click.echo(f"模型删除失败: {model_name}", err=True)
        
        return success

class OllamaInstallDefaultModelCommand(BaseCommand):
    """安装默认模型命令"""
    
    name = "install-default-model"
    help = "安装默认模型"
    group = "ollama"
    
    def run(self):
        """执行安装默认模型命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        click.echo("开始安装默认模型...")
        
        def callback(status):
            click.echo(f"  {status}")
        
        # 获取默认模型名称
        default_model = ollama_config.get('default_model', 'a3b-q8_0')
        click.echo(f"默认模型: {default_model}")
        
        success, message = ollama_manager.download_model(default_model, callback)
        
        if success:
            click.echo(f"默认模型安装成功: {default_model}")
        else:
            click.echo(f"默认模型安装失败: {message}", err=True)
        
        return success

class OllamaSetupCommand(BaseCommand):
    """完整设置Ollama命令"""
    
    name = "setup"
    help = "完整设置Ollama，包括安装、启动服务和下载默认模型"
    group = "ollama"
    
    def run(self):
        """执行完整设置Ollama命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        click.echo("开始完整设置Ollama...")
        
        # 检查Ollama是否已安装
        if not ollama_manager.check_ollama_installed():
            click.echo("1. 开始安装Ollama...")
            if not ollama_manager.download_ollama():
                click.echo("Ollama安装失败", err=True)
                return False
            click.echo("Ollama安装成功")
        else:
            click.echo("1. Ollama已安装")
        
        # 检查Ollama服务是否正在运行
        if not ollama_manager.check_ollama_running():
            click.echo("2. 开始启动Ollama服务...")
            if not ollama_manager.start_ollama_service():
                click.echo("Ollama服务启动失败", err=True)
                return False
            click.echo("Ollama服务启动成功")
        else:
            click.echo("2. Ollama服务已运行")
        
        # 检查默认模型是否已安装
        default_model = ollama_config.get('default_model', 'a3b-q8_0')
        if not ollama_manager.check_model_installed(default_model):
            click.echo(f"3. 开始下载默认模型 {default_model}...")
            
            def callback(status):
                click.echo(f"   {status}")
            
            success, message = ollama_manager.download_model(default_model, callback)
            if not success:
                click.echo(f"默认模型下载失败: {message}", err=True)
                return False
            click.echo(f"默认模型下载成功: {default_model}")
        else:
            click.echo(f"3. 默认模型 {default_model} 已安装")
        
        click.echo("\nOllama设置完成！")
        return True

class OllamaListModelsCommand(BaseCommand):
    """列出Ollama模型命令"""
    
    name = "list-models"
    help = "列出已安装的Ollama模型"
    group = "ollama"
    
    def run(self):
        """执行列出Ollama模型命令"""
        config = Config()
        ollama_config = config.install_settings.get('ollama', {})
        ollama_manager = OllamaManager(ollama_config)
        
        installed_models = ollama_manager.list_models()
        
        click.echo("已安装模型:")
        for model in installed_models:
            click.echo(f"- {model['name']} (大小: {model['size']}，修改时间: {model['modified_at']})")
        
        return installed_models
