#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.meeting_manager import MeetingManager
from HOS_ME.utils.report_generator import Config

class GenerateMeetingMinutesCommand(BaseCommand):
    """生成会议纪要命令"""
    
    name = "generate-minutes"
    help = "生成会议纪要"
    group = "meeting"
    group_help = "会议管理相关命令"
    
    params = [
        click.option('--topic', '-t', required=True, help='会议主题'),
        click.option('--participants', '-p', required=True, help='参会人员，用逗号分隔'),
        click.option('--date', '-d', help='会议日期，格式：YYYY-MM-DD'),
        click.option('--time', '-T', help='会议时间，格式：HH:MM'),
        click.option('--venue', '-v', help='会议地点'),
        click.option('--agenda', '-a', help='会议议程，用分号分隔'),
        click.option('--content', '-c', help='会议内容'),
        click.option('--output-file', '-o', help='输出文件路径'),
        click.option('--format', '-f', default='txt', help='输出格式，支持txt、docx、pdf等'),
    ]
    
    def run(self, topic, participants, date=None, time=None, venue='', agenda='', content='', output_file=None, format='txt'):
        """执行生成会议纪要命令"""
        config = Config()
        meeting_manager = MeetingManager(config)
        
        # 生成会议纪要
        minutes = meeting_manager.generate_meeting_minutes({
            'topic': topic,
            'participants': participants.split(','),
            'date': date,
            'time': time,
            'venue': venue,
            'agenda': agenda.split(';') if agenda else [],
            'content': content
        })
        
        # 处理输出
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minutes)
            click.echo(f"会议纪要已生成到: {output_file}")
        else:
            click.echo(minutes)
        
        return minutes

class CreateMeetingCommand(BaseCommand):
    """创建会议命令"""
    
    name = "create"
    help = "创建会议"
    group = "meeting"
    
    params = [
        click.option('--topic', '-t', required=True, help='会议主题'),
        click.option('--participants', '-p', required=True, help='参会人员，用逗号分隔'),
        click.option('--date', '-d', required=True, help='会议日期，格式：YYYY-MM-DD'),
        click.option('--time', '-T', required=True, help='会议时间，格式：HH:MM'),
        click.option('--duration', '-D', type=int, default=60, help='会议时长，单位：分钟'),
        click.option('--venue', '-v', help='会议地点'),
        click.option('--agenda', '-a', help='会议议程，用分号分隔'),
        click.option('--description', '-c', help='会议描述'),
    ]
    
    def run(self, topic, participants, date, time, duration=60, venue='', agenda='', description=''):
        """执行创建会议命令"""
        config = Config()
        meeting_manager = MeetingManager(config)
        
        # 创建会议
        meeting = meeting_manager.create_meeting({
            'topic': topic,
            'participants': participants.split(','),
            'date': date,
            'time': time,
            'duration': duration,
            'venue': venue,
            'agenda': agenda.split(';') if agenda else [],
            'description': description
        })
        
        click.echo(f"会议创建成功，ID: {meeting['id']}")
        return meeting

class ListMeetingsCommand(BaseCommand):
    """列出会议命令"""
    
    name = "list"
    help = "列出所有会议"
    group = "meeting"
    
    params = [
        click.option('--date', '-d', help='按日期筛选，格式：YYYY-MM-DD'),
        click.option('--status', '-s', help='按状态筛选，支持upcoming、completed、cancelled'),
    ]
    
    def run(self, date=None, status=None):
        """执行列出会议命令"""
        config = Config()
        meeting_manager = MeetingManager(config)
        
        # 获取会议列表
        meetings = meeting_manager.get_meetings()
        
        # 筛选会议
        if date:
            meetings = [m for m in meetings if m.get('date') == date]
        if status:
            meetings = [m for m in meetings if m.get('status') == status]
        
        click.echo("会议列表:")
        for meeting in meetings:
            click.echo(f"ID: {meeting['id']} - 主题: {meeting['topic']} - 日期: {meeting['date']} {meeting['time']} - 状态: {meeting.get('status', 'upcoming')}")
        
        return meetings
