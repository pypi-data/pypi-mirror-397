#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG库管理命令
"""

import click
from HOS_ME.cli.base import BaseCommand
from HOS_ME.utils.knowledge_base import KnowledgeBase
from HOS_ME.utils.report_generator import Config

class ListRagLibrariesCommand(BaseCommand):
    """列出RAG库命令"""
    
    name = "list"
    help = "列出所有RAG库"
    group = "rag"
    group_help = "RAG库管理相关命令"
    
    def run(self):
        """执行列出RAG库命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        libraries = knowledge_base.get_rag_libraries()
        
        click.echo("可用RAG库列表:")
        for library in libraries:
            click.echo(f"ID: {library['id']} - 名称: {library['name']} - 文档数: {len(library['documents'])} - 可见性: {library['visibility']}")
        
        return libraries

class CreateRagLibraryCommand(BaseCommand):
    """创建RAG库命令"""
    
    name = "create"
    help = "创建新RAG库"
    group = "rag"
    
    params = [
        click.option('--name', '-n', required=True, help='RAG库名称'),
        click.option('--description', '-d', help='RAG库描述'),
        click.option('--visibility', '-v', default='private', help='可见性，支持private、team、public'),
        click.option('--embedding-model', '-m', default='all-MiniLM-L6-v2', help='嵌入模型名称'),
    ]
    
    def run(self, name, description='', visibility='private', embedding_model='all-MiniLM-L6-v2'):
        """执行创建RAG库命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        library = knowledge_base.create_rag_library({
            'name': name,
            'description': description,
            'visibility': visibility,
            'embedding_model': embedding_model
        })
        click.echo(f"RAG库创建成功，ID: {library['id']}")
        return library

class DeleteRagLibraryCommand(BaseCommand):
    """删除RAG库命令"""
    
    name = "delete"
    help = "删除RAG库"
    group = "rag"
    
    params = [
        click.option('--id', '-i', required=True, help='RAG库ID'),
    ]
    
    def run(self, id):
        """执行删除RAG库命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        success = knowledge_base.delete_rag_library(id)
        if success:
            click.echo(f"RAG库删除成功，ID: {id}")
        else:
            click.echo(f"RAG库删除失败，ID: {id}", err=True)
        return success

class UploadDocumentToRagLibraryCommand(BaseCommand):
    """上传文档到RAG库命令"""
    
    name = "upload-document"
    help = "上传文档到RAG库"
    group = "rag"
    
    params = [
        click.option('--library-id', '-l', required=True, help='RAG库ID'),
        click.option('--file', '-f', required=True, help='文档文件路径'),
        click.option('--title', '-t', help='文档标题'),
        click.option('--description', '-d', help='文档描述'),
    ]
    
    def run(self, library_id, file, title=None, description=''):
        """执行上传文档到RAG库命令"""
        # 读取文件内容
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果没有提供标题，使用文件名
        if not title:
            import os
            title = os.path.basename(file)
        
        config = Config()
        knowledge_base = KnowledgeBase(config)
        
        # 创建文档
        document = knowledge_base.create_document({
            'title': title,
            'content': content,
            'description': description,
            'file_name': title
        })
        
        # 将文档添加到RAG库
        success = knowledge_base.add_document_to_rag_library(library_id, document['id'])
        if success:
            click.echo(f"文档上传成功，文档ID: {document['id']}，已添加到RAG库: {library_id}")
            return document
        else:
            click.echo(f"文档添加到RAG库失败，RAG库ID: {library_id}", err=True)
            return None

class ListDocumentsInRagLibraryCommand(BaseCommand):
    """列出RAG库中的文档命令"""
    
    name = "list-documents"
    help = "列出RAG库中的文档"
    group = "rag"
    
    params = [
        click.option('--library-id', '-l', required=True, help='RAG库ID'),
    ]
    
    def run(self, library_id):
        """执行列出RAG库中的文档命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        documents = knowledge_base.get_rag_library_documents(library_id)
        
        click.echo(f"RAG库 {library_id} 中的文档列表:")
        for document in documents:
            click.echo(f"ID: {document['id']} - 标题: {document['title']} - 总结: {document.get('summary', '')[:50]}...")
        
        return documents

class RemoveDocumentFromRagLibraryCommand(BaseCommand):
    """从RAG库移除文档命令"""
    
    name = "remove-document"
    help = "从RAG库移除文档"
    group = "rag"
    
    params = [
        click.option('--library-id', '-l', required=True, help='RAG库ID'),
        click.option('--document-id', '-d', required=True, help='文档ID'),
    ]
    
    def run(self, library_id, document_id):
        """执行从RAG库移除文档命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        success = knowledge_base.remove_document_from_rag_library(library_id, document_id)
        if success:
            click.echo(f"文档从RAG库移除成功，文档ID: {document_id}，RAG库ID: {library_id}")
        else:
            click.echo(f"文档从RAG库移除失败，文档ID: {document_id}，RAG库ID: {library_id}", err=True)
        return success

class UpdateDocumentSummariesCommand(BaseCommand):
    """更新文档总结命令"""
    
    name = "update-summaries"
    help = "更新所有文档的总结"
    group = "rag"
    
    def run(self):
        """执行更新所有文档总结命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        updated_count = knowledge_base.update_all_document_summaries()
        click.echo(f"已更新 {updated_count} 个文档的总结")
        return updated_count

class UpdateRagLibrarySummariesCommand(BaseCommand):
    """更新RAG库中文档总结命令"""
    
    name = "update-library-summaries"
    help = "更新RAG库中所有文档的总结"
    group = "rag"
    
    params = [
        click.option('--library-id', '-l', required=True, help='RAG库ID'),
    ]
    
    def run(self, library_id):
        """执行更新RAG库中文档总结命令"""
        config = Config()
        knowledge_base = KnowledgeBase(config)
        updated_count = knowledge_base.update_rag_library_summaries(library_id)
        click.echo(f"已更新RAG库 {library_id} 中的 {updated_count} 个文档的总结")
        return updated_count
