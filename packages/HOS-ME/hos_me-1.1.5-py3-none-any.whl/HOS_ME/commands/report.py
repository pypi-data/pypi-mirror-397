#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.report_generator import ReportGenerator
from HOS_ME.utils.api_client import APIClient
from HOS_ME.utils.template_manager import TemplateManager

class GenerateReportCommand(BaseCommand):
    """生成报告命令"""
    
    name = "generate"
    help = "生成报告"
    group = "report"
    group_help = "报告生成相关命令"
    
    params = [
        click.option('--prompt', '-p', required=True, help='生成报告的提示词'),
        click.option('--template-id', '-t', help='使用的模板ID'),
        click.option('--rag-library-id', '-r', help='使用的RAG库ID'),
        click.option('--output-file', '-o', help='输出文件路径'),
        click.option('--format', '-f', default='txt', help='输出格式，支持txt、docx、pdf等'),
    ]
    
    def run(self, prompt, template_id=None, rag_library_id=None, output_file=None, format='txt'):
        """执行生成报告命令"""
        # 初始化配置
        from HOS_ME.utils.report_generator import Config
        config = Config()
        
        # 初始化API客户端
        api_client = APIClient(config.api_key)
        
        # 初始化报告生成器
        report_generator = ReportGenerator(config, api_client)
        
        # 生成报告
        result = report_generator.generate_single_report(
            prompt=prompt,
            template_id=template_id,
            rag_library_id=rag_library_id
        )
        
        # 处理输出
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['report_content'])
            click.echo(f"报告已生成到: {output_file}")
        else:
            click.echo(result['report_content'])
        
        return result

class BatchGenerateReportCommand(BaseCommand):
    """批量生成报告命令"""
    
    name = "batch-generate"
    help = "批量生成报告"
    group = "report"
    
    params = [
        click.option('--prompts-file', '-f', required=True, help='包含多个提示词的文件路径，每行一个提示词'),
        click.option('--template-id', '-t', help='使用的模板ID'),
        click.option('--rag-library-id', '-r', help='使用的RAG库ID'),
        click.option('--output-dir', '-o', required=True, help='输出目录路径'),
        click.option('--format', '-F', default='txt', help='输出格式，支持txt、docx、pdf等'),
    ]
    
    def run(self, prompts_file, template_id=None, rag_library_id=None, output_dir=None, format='txt'):
        """执行批量生成报告命令"""
        # 初始化配置
        from HOS_ME.utils.report_generator import Config
        config = Config()
        
        # 初始化API客户端
        api_client = APIClient(config.api_key)
        
        # 初始化报告生成器
        report_generator = ReportGenerator(config, api_client)
        
        # 读取提示词文件
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        # 批量生成报告
        results = report_generator.generate_batch_reports(
            prompts=prompts,
            template_id=template_id,
            file_format=format,
            rag_library_id=rag_library_id
        )
        
        # 保存结果
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for i, result in enumerate(results):
            output_file = os.path.join(output_dir, f"report_{i+1}.{format}")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['report_content'])
            click.echo(f"报告已生成到: {output_file}")
        
        click.echo(f"批量生成完成，共生成 {len(results)} 份报告")
        return results
