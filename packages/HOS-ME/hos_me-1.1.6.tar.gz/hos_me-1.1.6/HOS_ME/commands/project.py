#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.project_manager import ProjectManager
from HOS_ME.utils.report_generator import Config

class CreateProjectCommand(BaseCommand):
    """创建项目命令"""
    
    name = "create"
    help = "创建新项目"
    group = "project"
    group_help = "项目管理相关命令"
    
    params = [
        click.option('--name', '-n', required=True, help='项目名称'),
        click.option('--description', '-d', help='项目描述'),
        click.option('--start-date', '-s', help='项目开始日期，格式：YYYY-MM-DD'),
        click.option('--end-date', '-e', help='项目结束日期，格式：YYYY-MM-DD'),
        click.option('--status', '-t', default='planning', help='项目状态：planning, in_progress, completed, on_hold'),
        click.option('--priority', '-p', default='medium', help='项目优先级：high, medium, low'),
        click.option('--manager', '-m', help='项目经理'),
        click.option('--members', '-M', help='项目成员，用逗号分隔'),
        click.option('--budget', '-b', type=float, default=0.0, help='项目预算'),
    ]
    
    def run(self, name, description='', start_date=None, end_date=None, status='planning', priority='medium', manager='', members='', budget=0.0):
        """执行创建项目命令"""
        project_manager = ProjectManager()
        
        # 创建项目数据
        project_data = {
            'name': name,
            'description': description,
            'status': status,
            'priority': priority,
            'manager': manager,
            'budget': budget
        }
        
        if start_date:
            project_data['start_date'] = start_date
        if end_date:
            project_data['end_date'] = end_date
        if members:
            project_data['members'] = members.split(',')
        
        # 创建项目
        project = project_manager.create_project(project_data)
        
        click.echo(f"项目创建成功，ID: {project['id']}")
        return project

class ListProjectsCommand(BaseCommand):
    """列出项目命令"""
    
    name = "list"
    help = "列出所有项目"
    group = "project"
    
    params = [
        click.option('--status', '-s', help='按状态筛选项目'),
        click.option('--manager', '-m', help='按项目经理筛选项目'),
        click.option('--member', '-M', help='按项目成员筛选项目'),
    ]
    
    def run(self, status=None, manager=None, member=None):
        """执行列出项目命令"""
        project_manager = ProjectManager()
        
        # 获取项目列表
        if status:
            projects = project_manager.get_projects_by_status(status)
        elif manager:
            projects = project_manager.get_projects_by_manager(manager)
        elif member:
            projects = project_manager.get_projects_by_member(member)
        else:
            projects = project_manager.get_projects()
        
        click.echo("项目列表:")
        for project in projects:
            click.echo(f"ID: {project['id']} - 名称: {project['name']} - 状态: {project['status']} - 进度: {project['progress']}% - 负责人: {project['manager']}")
        
        return projects

class GetProjectCommand(BaseCommand):
    """获取项目详情命令"""
    
    name = "get"
    help = "获取项目详情"
    group = "project"
    
    params = [
        click.argument('project_id', required=True, help='项目ID'),
    ]
    
    def run(self, project_id):
        """执行获取项目详情命令"""
        project_manager = ProjectManager()
        
        # 获取项目详情
        project = project_manager.get_project(project_id)
        
        if project:
            click.echo(f"项目ID: {project['id']}")
            click.echo(f"名称: {project['name']}")
            click.echo(f"描述: {project['description']}")
            click.echo(f"状态: {project['status']}")
            click.echo(f"优先级: {project['priority']}")
            click.echo(f"开始日期: {project['start_date']}")
            click.echo(f"结束日期: {project['end_date']}")
            click.echo(f"项目经理: {project['manager']}")
            click.echo(f"项目成员: {', '.join(project['members'])}")
            click.echo(f"预算: {project['budget']}")
            click.echo(f"进度: {project['progress']}%")
            click.echo(f"创建时间: {project['created_at']}")
            click.echo(f"更新时间: {project['updated_at']}")
        else:
            click.echo(f"项目 {project_id} 不存在")
        
        return project

class UpdateProjectCommand(BaseCommand):
    """更新项目命令"""
    
    name = "update"
    help = "更新项目信息"
    group = "project"
    
    params = [
        click.argument('project_id', required=True, help='项目ID'),
        click.option('--name', '-n', help='项目名称'),
        click.option('--description', '-d', help='项目描述'),
        click.option('--start-date', '-s', help='项目开始日期，格式：YYYY-MM-DD'),
        click.option('--end-date', '-e', help='项目结束日期，格式：YYYY-MM-DD'),
        click.option('--status', '-t', help='项目状态：planning, in_progress, completed, on_hold'),
        click.option('--priority', '-p', help='项目优先级：high, medium, low'),
        click.option('--manager', '-m', help='项目经理'),
        click.option('--members', '-M', help='项目成员，用逗号分隔'),
        click.option('--budget', '-b', type=float, help='项目预算'),
        click.option('--progress', '-P', type=int, help='项目进度，0-100'),
    ]
    
    def run(self, project_id, name=None, description=None, start_date=None, end_date=None, status=None, priority=None, manager=None, members=None, budget=None, progress=None):
        """执行更新项目命令"""
        project_manager = ProjectManager()
        
        # 准备更新数据
        update_data = {}
        if name:
            update_data['name'] = name
        if description:
            update_data['description'] = description
        if start_date:
            update_data['start_date'] = start_date
        if end_date:
            update_data['end_date'] = end_date
        if status:
            update_data['status'] = status
        if priority:
            update_data['priority'] = priority
        if manager:
            update_data['manager'] = manager
        if members:
            update_data['members'] = members.split(',')
        if budget is not None:
            update_data['budget'] = budget
        if progress is not None:
            update_data['progress'] = progress
        
        # 更新项目
        project = project_manager.update_project(project_id, update_data)
        
        if project:
            click.echo(f"项目 {project_id} 更新成功")
        else:
            click.echo(f"项目 {project_id} 不存在")
        
        return project

class DeleteProjectCommand(BaseCommand):
    """删除项目命令"""
    
    name = "delete"
    help = "删除项目"
    group = "project"
    
    params = [
        click.argument('project_id', required=True, help='项目ID'),
        click.option('--force', '-f', is_flag=True, help='强制删除，不提示'),
    ]
    
    def run(self, project_id, force=False):
        """执行删除项目命令"""
        project_manager = ProjectManager()
        
        # 确认删除
        if not force:
            if not click.confirm(f"确定要删除项目 {project_id} 吗？此操作不可恢复"):
                click.echo("删除操作已取消")
                return False
        
        # 删除项目
        success = project_manager.delete_project(project_id)
        
        if success:
            click.echo(f"项目 {project_id} 删除成功")
        else:
            click.echo(f"项目 {project_id} 不存在")
        
        return success

class GenerateProjectReportCommand(BaseCommand):
    """生成项目报告命令"""
    
    name = "generate-report"
    help = "生成项目报告"
    group = "project"
    
    params = [
        click.argument('project_id', required=True, help='项目ID'),
        click.option('--output-file', '-o', help='输出文件路径'),
    ]
    
    def run(self, project_id, output_file=None):
        """执行生成项目报告命令"""
        project_manager = ProjectManager()
        
        # 生成项目报告
        report = project_manager.generate_project_report(project_id)
        
        if report:
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"项目报告\n")
                    f.write(f"============\n\n")
                    f.write(f"报告日期: {report['report_date']}\n\n")
                    f.write(f"项目信息\n")
                    f.write(f"- 项目名称: {report['project']['name']}\n")
                    f.write(f"- 项目ID: {report['project']['id']}\n")
                    f.write(f"- 状态: {report['project']['status']}\n")
                    f.write(f"- 进度: {report['project']['progress']}%\n")
                    f.write(f"- 开始日期: {report['project']['start_date']}\n")
                    f.write(f"- 结束日期: {report['project']['end_date']}\n\n")
                    f.write(f"任务统计\n")
                    f.write(f"- 总任务数: {report['task_statistics']['total_tasks']}\n")
                    f.write(f"- 已完成任务: {report['task_statistics']['completed_tasks']}\n")
                    f.write(f"- 进行中任务: {report['task_statistics']['in_progress_tasks']}\n")
                    f.write(f"- 待处理任务: {report['task_statistics']['pending_tasks']}\n")
                    f.write(f"- 平均任务进度: {report['task_statistics']['avg_task_progress']}%\n\n")
                click.echo(f"项目报告已生成到: {output_file}")
            else:
                click.echo(f"项目报告\n")
                click.echo(f"报告日期: {report['report_date']}\n")
                click.echo(f"项目信息")
                click.echo(f"- 项目名称: {report['project']['name']}")
                click.echo(f"- 项目ID: {report['project']['id']}")
                click.echo(f"- 状态: {report['project']['status']}")
                click.echo(f"- 进度: {report['project']['progress']}%")
                click.echo(f"- 开始日期: {report['project']['start_date']}")
                click.echo(f"- 结束日期: {report['project']['end_date']}\n")
                click.echo(f"任务统计")
                click.echo(f"- 总任务数: {report['task_statistics']['total_tasks']}")
                click.echo(f"- 已完成任务: {report['task_statistics']['completed_tasks']}")
                click.echo(f"- 进行中任务: {report['task_statistics']['in_progress_tasks']}")
                click.echo(f"- 待处理任务: {report['task_statistics']['pending_tasks']}")
                click.echo(f"- 平均任务进度: {report['task_statistics']['avg_task_progress']}%")
        else:
            click.echo(f"项目 {project_id} 不存在")
        
        return report

class GetProjectStatisticsCommand(BaseCommand):
    """获取项目统计命令"""
    
    name = "stats"
    help = "获取项目统计信息"
    group = "project"
    
    def run(self):
        """执行获取项目统计命令"""
        project_manager = ProjectManager()
        
        # 获取项目统计
        stats = project_manager.get_project_statistics()
        
        click.echo("项目统计信息:")
        click.echo(f"- 总项目数: {stats['total_projects']}")
        click.echo(f"- 已完成项目: {stats['completed_projects']}")
        click.echo(f"- 进行中项目: {stats['in_progress_projects']}")
        click.echo(f"- 规划中项目: {stats['planning_projects']}")
        click.echo(f"- 暂停项目: {stats['on_hold_projects']}")
        click.echo(f"- 平均项目进度: {stats['avg_progress']}%")
        click.echo(f"- 总任务数: {stats['total_tasks']}")
        
        return stats