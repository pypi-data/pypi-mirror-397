#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审批管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.approval_manager import ApprovalManager

class CreateApprovalProcessCommand(BaseCommand):
    """创建审批流程命令"""
    
    name = "create-process"
    help = "创建审批流程"
    group = "approval"
    group_help = "审批管理相关命令"
    
    params = [
        click.option('--name', '-n', required=True, help='审批流程名称'),
        click.option('--description', '-d', help='审批流程描述'),
        click.option('--creator', '-c', help='创建者'),
        click.option('--active/--no-active', default=True, help='是否激活流程'),
    ]
    
    def run(self, name, description='', creator='', active=True):
        """执行创建审批流程命令"""
        approval_manager = ApprovalManager()
        
        # 创建审批流程数据
        process_data = {
            'name': name,
            'description': description,
            'creator': creator,
            'is_active': active
        }
        
        # 创建审批流程
        process = approval_manager.create_approval_process(process_data)
        
        click.echo(f"审批流程创建成功，ID: {process['id']}")
        return process

class ListApprovalProcessesCommand(BaseCommand):
    """列出审批流程命令"""
    
    name = "list-processes"
    help = "列出所有审批流程"
    group = "approval"
    
    def run(self):
        """执行列出审批流程命令"""
        approval_manager = ApprovalManager()
        
        # 获取审批流程列表
        processes = approval_manager.get_approval_processes()
        
        click.echo("审批流程列表:")
        for process in processes:
            status = "激活" if process['is_active'] else "未激活"
            click.echo(f"ID: {process['id']} - 名称: {process['name']} - 状态: {status} - 创建者: {process['creator']}")
        
        return processes

class CreateApprovalRequestCommand(BaseCommand):
    """创建审批请求命令"""
    
    name = "create-request"
    help = "创建审批请求"
    group = "approval"
    
    params = [
        click.option('--title', '-t', required=True, help='审批请求标题'),
        click.option('--description', '-d', help='审批请求描述'),
        click.option('--process-id', '-p', required=True, help='审批流程ID'),
        click.option('--requester', '-r', required=True, help='请求人'),
        click.option('--comments', '-c', help='审批请求备注'),
    ]
    
    def run(self, title, description='', process_id='', requester='', comments=''):
        """执行创建审批请求命令"""
        approval_manager = ApprovalManager()
        
        # 创建审批请求数据
        request_data = {
            'title': title,
            'description': description,
            'process_id': process_id,
            'requester': requester
        }
        
        if comments:
            request_data['comments'] = [{'content': comments}]
        
        # 创建审批请求
        request = approval_manager.create_approval_request(request_data)
        
        click.echo(f"审批请求创建成功，ID: {request['id']}")
        return request

class ListApprovalRequestsCommand(BaseCommand):
    """列出审批请求命令"""
    
    name = "list-requests"
    help = "列出所有审批请求"
    group = "approval"
    
    params = [
        click.option('--status', '-s', help='按状态筛选审批请求'),
        click.option('--requester', '-r', help='按请求人筛选审批请求'),
        click.option('--process-id', '-p', help='按审批流程ID筛选审批请求'),
    ]
    
    def run(self, status=None, requester=None, process_id=None):
        """执行列出审批请求命令"""
        approval_manager = ApprovalManager()
        
        # 准备筛选条件
        filters = {}
        if status:
            filters['status'] = status
        if requester:
            filters['requester'] = requester
        if process_id:
            filters['process_id'] = process_id
        
        # 获取审批请求列表
        requests = approval_manager.get_approval_requests(filters)
        
        click.echo("审批请求列表:")
        for request in requests:
            click.echo(f"ID: {request['id']} - 标题: {request['title']} - 状态: {request['status']} - 请求人: {request['requester']} - 流程: {request['process_name']}")
        
        return requests

class GetApprovalRequestCommand(BaseCommand):
    """获取审批请求详情命令"""
    
    name = "get-request"
    help = "获取审批请求详情"
    group = "approval"
    
    params = [
        click.argument('request_id', required=True, help='审批请求ID'),
    ]
    
    def run(self, request_id):
        """执行获取审批请求详情命令"""
        approval_manager = ApprovalManager()
        
        # 获取审批请求详情
        request = approval_manager.get_approval_request(request_id)
        
        if request:
            click.echo(f"审批请求ID: {request['id']}")
            click.echo(f"标题: {request['title']}")
            click.echo(f"描述: {request['description']}")
            click.echo(f"流程ID: {request['process_id']}")
            click.echo(f"流程名称: {request['process_name']}")
            click.echo(f"请求人: {request['requester']}")
            click.echo(f"状态: {request['status']}")
            click.echo(f"当前步骤: {request['current_step']}")
            click.echo(f"当前审批人: {', '.join(request['approvers'])}")
            click.echo(f"创建时间: {request['created_at']}")
            click.echo(f"更新时间: {request['updated_at']}")
        else:
            click.echo(f"审批请求 {request_id} 不存在")
        
        return request

class HandleApprovalCommand(BaseCommand):
    """处理审批命令"""
    
    name = "handle"
    help = "处理审批请求，支持批准、拒绝、转发、搁置等操作"
    group = "approval"
    
    params = [
        click.argument('request_id', required=True, help='审批请求ID'),
        click.argument('action', required=True, help='处理操作：approve, reject, forward, hold'),
        click.option('--approver', '-a', required=True, help='审批人'),
        click.option('--comments', '-c', help='审批备注'),
    ]
    
    def run(self, request_id, action, approver, comments=''):
        """执行处理审批命令"""
        approval_manager = ApprovalManager()
        
        # 处理审批数据
        action_data = {
            'action': action,
            'approver': approver,
            'comments': comments
        }
        
        # 处理审批
        request = approval_manager.handle_approval(request_id, action_data)
        
        if request:
            click.echo(f"审批请求 {request_id} 已处理，当前状态: {request['status']}")
        else:
            click.echo(f"审批请求 {request_id} 不存在或处理失败")
        
        return request

class ListApprovalRequestsByRequesterCommand(BaseCommand):
    """根据请求人列出审批请求命令"""
    
    name = "requests-by-requester"
    help = "根据请求人获取审批请求"
    group = "approval"
    
    params = [
        click.argument('requester', required=True, help='请求人'),
    ]
    
    def run(self, requester):
        """执行根据请求人列出审批请求命令"""
        approval_manager = ApprovalManager()
        
        # 获取审批请求列表
        requests = approval_manager.get_approval_requests_by_requester(requester)
        
        click.echo(f"请求人 {requester} 的审批请求列表:")
        for request in requests:
            click.echo(f"ID: {request['id']} - 标题: {request['title']} - 状态: {request['status']} - 流程: {request['process_name']}")
        
        return requests

class ListApprovalRequestsByApproverCommand(BaseCommand):
    """根据审批人列出审批请求命令"""
    
    name = "requests-by-approver"
    help = "根据审批人获取待处理的审批请求"
    group = "approval"
    
    params = [
        click.argument('approver', required=True, help='审批人'),
    ]
    
    def run(self, approver):
        """执行根据审批人列出审批请求命令"""
        approval_manager = ApprovalManager()
        
        # 获取审批请求列表
        requests = approval_manager.get_approval_requests_by_approver(approver)
        
        click.echo(f"审批人 {approver} 需要处理的审批请求列表:")
        for request in requests:
            click.echo(f"ID: {request['id']} - 标题: {request['title']} - 状态: {request['status']} - 流程: {request['process_name']}")
        
        return requests

class GetApprovalStatisticsCommand(BaseCommand):
    """获取审批统计命令"""
    
    name = "stats"
    help = "获取审批统计信息"
    group = "approval"
    
    def run(self):
        """执行获取审批统计命令"""
        approval_manager = ApprovalManager()
        
        # 获取审批统计
        stats = approval_manager.get_approval_statistics()
        
        click.echo("审批统计信息:")
        click.echo(f"- 总请求数: {stats['total_requests']}")
        click.echo("\n按状态统计:")
        for status, count in stats['status_stats'].items():
            click.echo(f"- {status}: {count}")
        click.echo("\n按流程统计:")
        for process, count in stats['process_stats'].items():
            click.echo(f"- {process}: {count}")
        
        return stats