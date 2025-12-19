#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.template_manager import TemplateManager

class ListTemplatesCommand(BaseCommand):
    """列出模板命令"""
    
    name = "list"
    help = "列出所有模板"
    group = "template"
    group_help = "模板管理相关命令"
    
    def run(self):
        """执行列出模板命令"""
        template_manager = TemplateManager()
        templates = template_manager.get_templates()
        
        click.echo("可用模板列表:")
        for template in templates:
            click.echo(f"ID: {template['id']} - 名称: {template['name']} - 类型: {template['type']}")
        
        return templates

class CreateTemplateCommand(BaseCommand):
    """创建模板命令"""
    
    name = "create"
    help = "创建新模板"
    group = "template"
    
    params = [
        click.option('--name', '-n', required=True, help='模板名称'),
        click.option('--content', '-c', required=True, help='模板内容'),
        click.option('--type', '-t', default='default', help='模板类型'),
        click.option('--description', '-d', help='模板描述'),
        click.option('--output-format', '-f', default='txt', help='默认输出格式'),
    ]
    
    def run(self, name, content, type='default', description='', output_format='txt'):
        """执行创建模板命令"""
        template_manager = TemplateManager()
        template = template_manager.create_template(name, content, type, description, output_format)
        click.echo(f"模板创建成功，ID: {template['id']}")
        return template

class UpdateTemplateCommand(BaseCommand):
    """更新模板命令"""
    
    name = "update"
    help = "更新现有模板"
    group = "template"
    
    params = [
        click.option('--id', '-i', required=True, help='模板ID'),
        click.option('--name', '-n', help='模板名称'),
        click.option('--content', '-c', help='模板内容'),
        click.option('--type', '-t', help='模板类型'),
        click.option('--description', '-d', help='模板描述'),
        click.option('--output-format', '-f', help='默认输出格式'),
    ]
    
    def run(self, id, name=None, content=None, type=None, description=None, output_format=None):
        """执行更新模板命令"""
        template_manager = TemplateManager()
        template = template_manager.update_template(
            template_id=id,
            name=name,
            content=content,
            template_type=type,
            description=description,
            output_format=output_format
        )
        click.echo(f"模板更新成功，ID: {template['id']}")
        return template

class DeleteTemplateCommand(BaseCommand):
    """删除模板命令"""
    
    name = "delete"
    help = "删除模板"
    group = "template"
    
    params = [
        click.option('--id', '-i', required=True, help='模板ID'),
    ]
    
    def run(self, id):
        """执行删除模板命令"""
        template_manager = TemplateManager()
        template_manager.delete_template(id)
        click.echo(f"模板删除成功，ID: {id}")
        return True

class SetCurrentTemplateCommand(BaseCommand):
    """设置当前模板命令"""
    
    name = "set-current"
    help = "设置当前使用的模板"
    group = "template"
    
    params = [
        click.option('--id', '-i', required=True, help='模板ID'),
    ]
    
    def run(self, id):
        """执行设置当前模板命令"""
        template_manager = TemplateManager()
        template_manager.set_current_template(id)
        click.echo(f"当前模板已设置为: {id}")
        return True

class ExportTemplateCommand(BaseCommand):
    """导出模板命令"""
    
    name = "export"
    help = "导出模板为文件"
    group = "template"
    
    params = [
        click.option('--id', '-i', required=True, help='模板ID'),
        click.option('--output-file', '-o', required=True, help='输出文件路径'),
    ]
    
    def run(self, id, output_file):
        """执行导出模板命令"""
        template_manager = TemplateManager()
        template = template_manager.get_template(id)
        if not template:
            click.echo(f"模板不存在，ID: {id}", err=True)
            return False
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        click.echo(f"模板导出成功，文件: {output_file}")
        return True

class ImportTemplateCommand(BaseCommand):
    """导入模板命令"""
    
    name = "import"
    help = "从文件导入模板"
    group = "template"
    
    params = [
        click.option('--input-file', '-i', required=True, help='输入文件路径'),
    ]
    
    def run(self, input_file):
        """执行导入模板命令"""
        import json
        with open(input_file, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        template_manager = TemplateManager()
        template = template_manager.create_template(
            name=template_data['name'],
            content=template_data['content'],
            template_type=template_data.get('type', 'default'),
            description=template_data.get('description', ''),
            output_format=template_data.get('output_format', 'txt')
        )
        
        click.echo(f"模板导入成功，ID: {template['id']}")
        return template
