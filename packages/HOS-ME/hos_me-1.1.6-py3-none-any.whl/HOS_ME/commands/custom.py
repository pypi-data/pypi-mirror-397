#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义模块和工作流管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.report_generator import Config

class ListCustomModulesCommand(BaseCommand):
    """列出自定义模块命令"""
    
    name = "list-modules"
    help = "列出所有自定义模块"
    group = "custom"
    group_help = "自定义模块和工作流管理相关命令"
    
    def run(self):
        """执行列出自定义模块命令"""
        config = Config()
        
        # 获取自定义模块列表
        modules = config.get_custom_modules()
        
        click.echo("自定义模块列表:")
        for module in modules:
            click.echo(f"ID: {module['id']} - 名称: {module['name']} - 类型: {module.get('type', 'unknown')} - 创建时间: {module['created_at']}")
        
        return modules

class CreateCustomModuleCommand(BaseCommand):
    """创建自定义模块命令"""
    
    name = "create-module"
    help = "创建自定义模块"
    group = "custom"
    
    params = [
        click.option('--name', '-n', required=True, help='模块名称'),
        click.option('--description', '-d', help='模块描述'),
        click.option('--type', '-t', default='workflow_module', help='模块类型'),
        click.option('--workflow-id', '-w', help='关联的工作流ID'),
    ]
    
    def run(self, name, description='', type='workflow_module', workflow_id=''):
        """执行创建自定义模块命令"""
        config = Config()
        
        # 创建模块数据
        module_data = {
            'name': name,
            'description': description,
            'type': type
        }
        
        if workflow_id:
            # 获取工作流
            workflows = config.get_workflows()
            workflow = next((w for w in workflows if w['id'] == workflow_id), None)
            if workflow:
                module_data['workflow_id'] = workflow_id
                module_data['workflow_config'] = {
                    'steps': workflow.get('steps', []),
                    'settings': workflow.get('settings', {})
                }
        
        # 创建模块
        module = config.add_custom_module(module_data)
        
        click.echo(f"自定义模块创建成功，ID: {module['id']}")
        return module

class DeleteCustomModuleCommand(BaseCommand):
    """删除自定义模块命令"""
    
    name = "delete-module"
    help = "删除自定义模块"
    group = "custom"
    
    params = [
        click.argument('module_id', required=True, help='模块ID'),
        click.option('--force', '-f', is_flag=True, help='强制删除，不提示'),
    ]
    
    def run(self, module_id, force=False):
        """执行删除自定义模块命令"""
        config = Config()
        
        # 确认删除
        if not force:
            if not click.confirm(f"确定要删除模块 {module_id} 吗？此操作不可恢复"):
                click.echo("删除操作已取消")
                return False
        
        # 删除模块
        config.delete_custom_module(module_id)
        
        click.echo(f"自定义模块 {module_id} 删除成功")
        return True

class ListWorkflowsCommand(BaseCommand):
    """列出工作流命令"""
    
    name = "list-workflows"
    help = "列出所有工作流"
    group = "custom"
    
    def run(self):
        """执行列出工作流命令"""
        config = Config()
        
        # 获取工作流列表
        workflows = config.get_workflows()
        
        click.echo("工作流列表:")
        for workflow in workflows:
            click.echo(f"ID: {workflow['id']} - 名称: {workflow['name']} - 创建时间: {workflow['created_at']}")
        
        return workflows

class CreateWorkflowCommand(BaseCommand):
    """创建工作流命令"""
    
    name = "create-workflow"
    help = "创建工作流"
    group = "custom"
    
    params = [
        click.option('--name', '-n', required=True, help='工作流名称'),
        click.option('--description', '-d', help='工作流描述'),
    ]
    
    def run(self, name, description=''):
        """执行创建工作流命令"""
        config = Config()
        
        # 创建工作流数据
        workflow_data = {
            'name': name,
            'description': description,
            'steps': []
        }
        
        # 创建工作流
        workflow = config.add_workflow(workflow_data)
        
        click.echo(f"工作流创建成功，ID: {workflow['id']}")
        return workflow

class DeleteWorkflowCommand(BaseCommand):
    """删除工作流命令"""
    
    name = "delete-workflow"
    help = "删除工作流"
    group = "custom"
    
    params = [
        click.argument('workflow_id', required=True, help='工作流ID'),
        click.option('--force', '-f', is_flag=True, help='强制删除，不提示'),
    ]
    
    def run(self, workflow_id, force=False):
        """执行删除工作流命令"""
        config = Config()
        
        # 确认删除
        if not force:
            if not click.confirm(f"确定要删除工作流 {workflow_id} 吗？此操作不可恢复"):
                click.echo("删除操作已取消")
                return False
        
        # 删除工作流
        config.delete_workflow(workflow_id)
        
        click.echo(f"工作流 {workflow_id} 删除成功")
        return True

class GenerateWorkflowCommand(BaseCommand):
    """生成工作流命令"""
    
    name = "generate-workflow"
    help = "基于提示词生成工作流"
    group = "custom"
    
    params = [
        click.argument('prompt', required=True, help='工作流需求描述'),
        click.option('--save', '-s', is_flag=True, help='保存生成的工作流'),
    ]
    
    def run(self, prompt, save=False):
        """执行生成工作流命令"""
        config = Config()
        
        # 生成工作流
        workflow = config.generate_workflow(prompt)
        
        click.echo("生成的工作流:")
        click.echo(f"名称: {workflow['name']}")
        click.echo(f"描述: {workflow['description']}")
        click.echo("步骤:")
        for step in workflow['steps']:
            click.echo(f"  - {step['name']} ({step['action']})")
        
        if save:
            # 保存工作流
            saved_workflow = config.add_workflow(workflow)
            click.echo(f"工作流已保存，ID: {saved_workflow['id']}")
            return saved_workflow
        
        return workflow

class ConvertWorkflowToModuleCommand(BaseCommand):
    """将工作流转换为模块命令"""
    
    name = "convert-workflow-to-module"
    help = "将工作流转换为自定义模块"
    group = "custom"
    
    params = [
        click.argument('workflow_id', required=True, help='工作流ID'),
    ]
    
    def run(self, workflow_id):
        """执行将工作流转换为模块命令"""
        config = Config()
        
        # 转换工作流为模块
        module = config.convert_workflow_to_module(workflow_id)
        
        if module:
            click.echo(f"工作流转换为模块成功，模块ID: {module['id']}")
        else:
            click.echo(f"转换失败，工作流 {workflow_id} 不存在")
        
        return module