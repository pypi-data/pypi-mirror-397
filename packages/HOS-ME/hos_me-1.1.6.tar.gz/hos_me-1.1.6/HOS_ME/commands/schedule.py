#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日程管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.schedule_manager import ScheduleManager

class CreateScheduleCommand(BaseCommand):
    """创建日程命令"""
    
    name = "create"
    help = "创建新日程"
    group = "schedule"
    group_help = "日程管理相关命令"
    
    params = [
        click.option('--title', '-t', required=True, help='日程标题'),
        click.option('--description', '-d', help='日程描述'),
        click.option('--type', '-T', default='meeting', help='日程类型：meeting, appointment, event, deadline, reminder'),
        click.option('--start-time', '-s', help='开始时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--end-time', '-e', help='结束时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--location', '-l', help='日程地点'),
        click.option('--organizer', '-o', help='组织者'),
        click.option('--attendees', '-a', help='参会人员，用逗号分隔'),
        click.option('--status', '-S', default='planned', help='日程状态：planned, in_progress, completed, canceled, postponed'),
    ]
    
    def run(self, title, description='', type='meeting', start_time=None, end_time=None, location='', organizer='', attendees='', status='planned'):
        """执行创建日程命令"""
        schedule_manager = ScheduleManager()
        
        # 创建日程数据
        schedule_data = {
            'title': title,
            'description': description,
            'type': type,
            'status': status,
            'location': location,
            'organizer': organizer
        }
        
        if start_time:
            schedule_data['start_time'] = start_time
        if end_time:
            schedule_data['end_time'] = end_time
        if attendees:
            schedule_data['attendees'] = attendees.split(',')
        
        # 创建日程
        schedule = schedule_manager.create_schedule(schedule_data)
        
        click.echo(f"日程创建成功，ID: {schedule['id']}")
        return schedule

class ListSchedulesCommand(BaseCommand):
    """列出日程命令"""
    
    name = "list"
    help = "列出所有日程"
    group = "schedule"
    
    params = [
        click.option('--type', '-t', help='按类型筛选日程'),
        click.option('--status', '-s', help='按状态筛选日程'),
        click.option('--organizer', '-o', help='按组织者筛选日程'),
        click.option('--attendee', '-a', help='按参会人员筛选日程'),
        click.option('--start-date', '-S', help='按开始日期筛选日程，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--end-date', '-E', help='按结束日期筛选日程，格式：YYYY-MM-DD HH:MM:SS'),
    ]
    
    def run(self, type=None, status=None, organizer=None, attendee=None, start_date=None, end_date=None):
        """执行列出日程命令"""
        schedule_manager = ScheduleManager()
        
        # 准备筛选条件
        filters = {}
        if type:
            filters['type'] = type
        if status:
            filters['status'] = status
        if organizer:
            filters['organizer'] = organizer
        if attendee:
            filters['attendee'] = attendee
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        # 获取日程列表
        schedules = schedule_manager.get_schedules(filters)
        
        click.echo("日程列表:")
        for schedule in schedules:
            click.echo(f"ID: {schedule['id']} - 标题: {schedule['title']} - 类型: {schedule['type']} - 状态: {schedule['status']} - 开始时间: {schedule['start_time']}")
        
        return schedules

class GetScheduleCommand(BaseCommand):
    """获取日程详情命令"""
    
    name = "get"
    help = "获取日程详情"
    group = "schedule"
    
    params = [
        click.argument('schedule_id', required=True, help='日程ID'),
    ]
    
    def run(self, schedule_id):
        """执行获取日程详情命令"""
        schedule_manager = ScheduleManager()
        
        # 获取日程详情
        schedule = schedule_manager.get_schedule(schedule_id)
        
        if schedule:
            click.echo(f"日程ID: {schedule['id']}")
            click.echo(f"标题: {schedule['title']}")
            click.echo(f"描述: {schedule['description']}")
            click.echo(f"类型: {schedule['type']}")
            click.echo(f"状态: {schedule['status']}")
            click.echo(f"开始时间: {schedule['start_time']}")
            click.echo(f"结束时间: {schedule['end_time']}")
            click.echo(f"地点: {schedule['location']}")
            click.echo(f"组织者: {schedule['organizer']}")
            click.echo(f"参会人员: {', '.join(schedule['attendees'])}")
            click.echo(f"创建时间: {schedule['created_at']}")
            click.echo(f"更新时间: {schedule['updated_at']}")
        else:
            click.echo(f"日程 {schedule_id} 不存在")
        
        return schedule

class UpdateScheduleCommand(BaseCommand):
    """更新日程命令"""
    
    name = "update"
    help = "更新日程信息"
    group = "schedule"
    
    params = [
        click.argument('schedule_id', required=True, help='日程ID'),
        click.option('--title', '-t', help='日程标题'),
        click.option('--description', '-d', help='日程描述'),
        click.option('--type', '-T', help='日程类型'),
        click.option('--start-time', '-s', help='开始时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--end-time', '-e', help='结束时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--location', '-l', help='日程地点'),
        click.option('--organizer', '-o', help='组织者'),
        click.option('--status', '-S', help='日程状态'),
    ]
    
    def run(self, schedule_id, title=None, description=None, type=None, start_time=None, end_time=None, location=None, organizer=None, status=None):
        """执行更新日程命令"""
        schedule_manager = ScheduleManager()
        
        # 准备更新数据
        update_data = {}
        if title:
            update_data['title'] = title
        if description:
            update_data['description'] = description
        if type:
            update_data['type'] = type
        if start_time:
            update_data['start_time'] = start_time
        if end_time:
            update_data['end_time'] = end_time
        if location:
            update_data['location'] = location
        if organizer:
            update_data['organizer'] = organizer
        if status:
            update_data['status'] = status
        
        # 更新日程
        schedule = schedule_manager.update_schedule(schedule_id, update_data)
        
        if schedule:
            click.echo(f"日程 {schedule_id} 更新成功")
        else:
            click.echo(f"日程 {schedule_id} 不存在")
        
        return schedule

class DeleteScheduleCommand(BaseCommand):
    """删除日程命令"""
    
    name = "delete"
    help = "删除日程"
    group = "schedule"
    
    params = [
        click.argument('schedule_id', required=True, help='日程ID'),
    ]
    
    def run(self, schedule_id):
        """执行删除日程命令"""
        schedule_manager = ScheduleManager()
        
        # 删除日程
        success = schedule_manager.delete_schedule(schedule_id)
        
        if success:
            click.echo(f"日程 {schedule_id} 删除成功")
        else:
            click.echo(f"日程 {schedule_id} 不存在")
        
        return success

class AddAttendeeCommand(BaseCommand):
    """添加参会人员命令"""
    
    name = "add-attendee"
    help = "添加参会人员到日程"
    group = "schedule"
    
    params = [
        click.argument('schedule_id', required=True, help='日程ID'),
        click.argument('attendee', required=True, help='参会人员'),
    ]
    
    def run(self, schedule_id, attendee):
        """执行添加参会人员命令"""
        schedule_manager = ScheduleManager()
        
        # 添加参会人员
        schedule = schedule_manager.add_attendee(schedule_id, attendee)
        
        if schedule:
            click.echo(f"参会人员 {attendee} 已添加到日程 {schedule_id}")
        else:
            click.echo(f"日程 {schedule_id} 不存在")
        
        return schedule

class RemoveAttendeeCommand(BaseCommand):
    """移除参会人员命令"""
    
    name = "remove-attendee"
    help = "从日程移除参会人员"
    group = "schedule"
    
    params = [
        click.argument('schedule_id', required=True, help='日程ID'),
        click.argument('attendee', required=True, help='参会人员'),
    ]
    
    def run(self, schedule_id, attendee):
        """执行移除参会人员命令"""
        schedule_manager = ScheduleManager()
        
        # 移除参会人员
        schedule = schedule_manager.remove_attendee(schedule_id, attendee)
        
        if schedule:
            click.echo(f"参会人员 {attendee} 已从日程 {schedule_id} 移除")
        else:
            click.echo(f"日程 {schedule_id} 不存在")
        
        return schedule

class GetTodaysSchedulesCommand(BaseCommand):
    """获取今日日程命令"""
    
    name = "today"
    help = "获取今日日程"
    group = "schedule"
    
    def run(self):
        """执行获取今日日程命令"""
        schedule_manager = ScheduleManager()
        
        # 获取今日日程
        schedules = schedule_manager.get_todays_schedules()
        
        click.echo("今日日程:")
        for schedule in schedules:
            click.echo(f"ID: {schedule['id']} - 标题: {schedule['title']} - 类型: {schedule['type']} - 开始时间: {schedule['start_time']} - 地点: {schedule['location']}")
        
        return schedules

class GetUpcomingSchedulesCommand(BaseCommand):
    """获取即将到来的日程命令"""
    
    name = "upcoming"
    help = "获取即将到来的日程"
    group = "schedule"
    
    params = [
        click.option('--days', '-d', type=int, default=7, help='未来几天的日程，默认7天'),
    ]
    
    def run(self, days=7):
        """执行获取即将到来的日程命令"""
        schedule_manager = ScheduleManager()
        
        # 获取即将到来的日程
        schedules = schedule_manager.get_upcoming_schedules(days)
        
        click.echo(f"未来 {days} 天的日程:")
        for schedule in schedules:
            click.echo(f"ID: {schedule['id']} - 标题: {schedule['title']} - 类型: {schedule['type']} - 开始时间: {schedule['start_time']} - 地点: {schedule['location']}")
        
        return schedules

class CheckScheduleConflictCommand(BaseCommand):
    """检查日程冲突命令"""
    
    name = "check-conflict"
    help = "检查日程时间冲突"
    group = "schedule"
    
    params = [
        click.option('--start-time', '-s', required=True, help='开始时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--end-time', '-e', required=True, help='结束时间，格式：YYYY-MM-DD HH:MM:SS'),
        click.option('--exclude-id', '-x', help='排除的日程ID，用于更新日程时避免与自身冲突'),
    ]
    
    def run(self, start_time, end_time, exclude_id=None):
        """执行检查日程冲突命令"""
        schedule_manager = ScheduleManager()
        
        # 检查日程冲突
        conflicts = schedule_manager.check_schedule_conflict(start_time, end_time, exclude_id)
        
        if conflicts:
            click.echo(f"发现 {len(conflicts)} 个冲突日程:")
            for conflict in conflicts:
                click.echo(f"ID: {conflict['id']} - 标题: {conflict['title']} - 开始时间: {conflict['start_time']} - 结束时间: {conflict['end_time']}")
        else:
            click.echo("未发现冲突日程")
        
        return conflicts

class GetScheduleStatisticsCommand(BaseCommand):
    """获取日程统计命令"""
    
    name = "stats"
    help = "获取日程统计信息"
    group = "schedule"
    
    def run(self):
        """执行获取日程统计命令"""
        schedule_manager = ScheduleManager()
        
        # 获取日程统计
        stats = schedule_manager.get_schedule_statistics()
        
        click.echo("日程统计信息:")
        click.echo(f"- 总日程数: {stats['total_schedules']}")
        click.echo(f"- 今日日程: {stats['todays_schedules']}")
        click.echo(f"- 未来7天日程: {stats['upcoming_schedules']}")
        click.echo("\n按类型统计:")
        for type_name, count in stats['type_stats'].items():
            click.echo(f"- {type_name}: {count}")
        click.echo("\n按状态统计:")
        for status_name, count in stats['status_stats'].items():
            click.echo(f"- {status_name}: {count}")
        
        return stats