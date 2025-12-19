#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.task_manager import TaskManager

class ListTasksCommand(BaseCommand):
    """列出任务命令"""
    
    name = "list"
    help = "列出所有任务"
    group = "task"
    group_help = "任务管理相关命令"
    
    def run(self):
        """执行列出任务命令"""
        task_manager = TaskManager()
        
        # 获取所有任务
        tasks = task_manager.get_all_tasks()
        
        click.echo("任务列表:")
        for task in tasks:
            click.echo(f"ID: {task['id']} - 类型: {task['type']} - 状态: {task['status']} - 进度: {task['percentage']}% - 描述: {task['description']}")
        
        return tasks

class GetTaskCommand(BaseCommand):
    """获取任务详情命令"""
    
    name = "get"
    help = "获取任务详情"
    group = "task"
    
    params = [
        click.argument('task_id', required=True, help='任务ID'),
    ]
    
    def run(self, task_id):
        """执行获取任务详情命令"""
        task_manager = TaskManager()
        
        # 获取任务详情
        task = task_manager.get_task(task_id)
        
        if task:
            click.echo(f"任务ID: {task['id']}")
            click.echo(f"类型: {task['type']}")
            click.echo(f"描述: {task['description']}")
            click.echo(f"状态: {task['status']}")
            click.echo(f"进度: {task['percentage']}%")
            click.echo(f"当前步骤: {task['current_step']}/{task['total_steps']}")
            click.echo(f"创建时间: {task['created_at']}")
            click.echo(f"开始时间: {task['started_at']}")
            click.echo(f"更新时间: {task['updated_at']}")
            if task['result']:
                click.echo(f"结果: {task['result']}")
            if task['error']:
                click.echo(f"错误: {task['error']}")
        else:
            click.echo(f"任务 {task_id} 不存在")
        
        return task

class PauseTaskCommand(BaseCommand):
    """暂停任务命令"""
    
    name = "pause"
    help = "暂停任务"
    group = "task"
    
    params = [
        click.argument('task_id', required=True, help='任务ID'),
    ]
    
    def run(self, task_id):
        """执行暂停任务命令"""
        task_manager = TaskManager()
        
        # 暂停任务
        success = task_manager.pause_task(task_id)
        
        if success:
            click.echo(f"任务 {task_id} 已暂停")
        else:
            click.echo(f"无法暂停任务 {task_id}，可能任务不存在")
        
        return success

class ResumeTaskCommand(BaseCommand):
    """恢复任务命令"""
    
    name = "resume"
    help = "恢复任务"
    group = "task"
    
    params = [
        click.argument('task_id', required=True, help='任务ID'),
    ]
    
    def run(self, task_id):
        """执行恢复任务命令"""
        task_manager = TaskManager()
        
        # 恢复任务
        success = task_manager.resume_task(task_id)
        
        if success:
            click.echo(f"任务 {task_id} 已恢复")
        else:
            click.echo(f"无法恢复任务 {task_id}，可能任务不存在")
        
        return success

class CancelTaskCommand(BaseCommand):
    """取消任务命令"""
    
    name = "cancel"
    help = "取消任务"
    group = "task"
    
    params = [
        click.argument('task_id', required=True, help='任务ID'),
    ]
    
    def run(self, task_id):
        """执行取消任务命令"""
        task_manager = TaskManager()
        
        # 取消任务
        success = task_manager.cancel_task(task_id)
        
        if success:
            click.echo(f"任务 {task_id} 已取消")
        else:
            click.echo(f"无法取消任务 {task_id}，可能任务不存在")
        
        return success

class CleanupTasksCommand(BaseCommand):
    """清理已完成任务命令"""
    
    name = "cleanup"
    help = "清理已完成、失败或取消的任务"
    group = "task"
    
    def run(self):
        """执行清理任务命令"""
        task_manager = TaskManager()
        
        # 清理已完成的任务
        task_manager.cleanup_completed_tasks()
        
        click.echo("已清理所有已完成、失败或取消的任务")
        return True