import os
import json
import time
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# 全局模型实例，避免重复加载
_embedding_model = None

def get_embedding_model():
    """获取嵌入模型（单例模式）"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

class KnowledgeBase:
    def __init__(self, config=None):
        self.knowledge_dir = os.path.join(os.getcwd(), "knowledge_base")
        self.documents_file = os.path.join(self.knowledge_dir, "documents.json")
        self.categories_file = os.path.join(self.knowledge_dir, "categories.json")
        self.tags_file = os.path.join(self.knowledge_dir, "tags.json")
        self.document_versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        self.permissions_file = os.path.join(self.knowledge_dir, "permissions.json")
        # RAG库相关文件
        self.rag_libraries_file = os.path.join(self.knowledge_dir, "rag_libraries.json")
        self.rag_embeddings_dir = os.path.join(self.knowledge_dir, "rag_embeddings")
        
        # 系统配置
        self.config = config
        
        # 确保目录存在
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(os.path.join(self.knowledge_dir, "files"), exist_ok=True)
        os.makedirs(self.rag_embeddings_dir, exist_ok=True)
        
        # 初始化数据
        self.documents = self._load_documents()
        self.categories = self._load_categories()
        self.tags = self._load_tags()
        self.document_versions = self._load_document_versions()
        self.permissions = self._load_permissions()
        self.rag_libraries = self._load_rag_libraries()
        # 缓存嵌入模型
        self.embedding_model = get_embedding_model()
        
        # 获取RAG总结配置
        self.rag_summary_settings = {
            "enabled": True,
            "max_chars": 100,
            "include_filename": True,
            "include_content_preview": True
        }
        
        if self.config and hasattr(self.config, 'system_settings'):
            self.rag_summary_settings.update(
                self.config.system_settings.get("rag_settings", {}).get("summary_settings", {})
            )
    
    def _load_documents(self):
        """加载文档数据"""
        if os.path.exists(self.documents_file):
            with open(self.documents_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_documents(self):
        """保存文档数据"""
        with open(self.documents_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self):
        """加载分类数据"""
        if os.path.exists(self.categories_file):
            with open(self.categories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_categories(self):
        """保存分类数据"""
        with open(self.categories_file, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
    
    def _load_tags(self):
        """加载标签数据"""
        if os.path.exists(self.tags_file):
            with open(self.tags_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_tags(self):
        """保存标签数据"""
        with open(self.tags_file, "w", encoding="utf-8") as f:
            json.dump(self.tags, f, ensure_ascii=False, indent=2)
    
    def generate_file_summary(self, filename, content, max_chars=None):
        """根据文件名和内容生成文件总结
        
        Args:
            filename (str): 文件名
            content (str): 文件内容
            max_chars (int): 最大读取字符数（可选，默认使用系统设置）
            
        Returns:
            str: 生成的文件总结
        """
        # 使用系统设置或传入的max_chars
        if max_chars is None:
            max_chars = self.rag_summary_settings.get("max_chars", 100)
        
        # 获取文件的前max_chars字符
        preview_content = content[:max_chars]
        
        # 生成总结
        summary = ""
        
        if self.rag_summary_settings.get("include_filename", True):
            summary += f"文件 {filename}"
            if self.rag_summary_settings.get("include_content_preview", True):
                summary += f" 包含以下内容：{preview_content}"
        elif self.rag_summary_settings.get("include_content_preview", True):
            summary += f"内容：{preview_content}"
        
        if len(content) > max_chars:
            summary += "... (内容过长，仅显示部分)"
        
        return summary
    
    def create_document(self, document_data):
        """创建文档"""
        # 生成唯一ID
        document_id = f"doc_{int(time.time())}"
        
        # 获取文档内容
        content = document_data.get("content", "")
        filename = document_data.get("file_name", "新建文档")
        
        # 生成文件总结（使用系统设置）
        summary = self.generate_file_summary(filename, content)
        
        # 创建文档对象
        document = {
            "id": document_id,
            "title": document_data.get("title", "新建文档"),
            "content": content,
            "summary": summary,
            "category_id": document_data.get("category_id", ""),
            "tags": document_data.get("tags", []),
            "author": document_data.get("author", ""),
            "file_path": document_data.get("file_path", ""),
            "file_name": filename,
            "file_type": document_data.get("file_type", ""),
            "version": 1,
            "status": document_data.get("status", "draft"),  # draft, published, archived
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "views": 0,
            "likes": 0
        }
        
        # 添加到文档列表
        self.documents.append(document)
        self._save_documents()
        
        return document
    
    def get_documents(self):
        """获取所有文档"""
        return self.documents
    
    def get_document(self, document_id):
        """获取指定文档"""
        return next((d for d in self.documents if d["id"] == document_id), None)
    
    def update_document(self, document_id, document_data):
        """更新文档"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 更新文档数据
                self.documents[i].update(document_data)
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_documents()
                return self.documents[i]
        return None
    
    def delete_document(self, document_id):
        """删除文档"""
        self.documents = [d for d in self.documents if d["id"] != document_id]
        self._save_documents()
        return True
    
    def search_documents(self, query):
        """搜索文档"""
        results = []
        query_lower = query.lower()
        
        for document in self.documents:
            # 在标题、内容、标签中搜索
            if (query_lower in document["title"].lower() or 
                query_lower in document["content"].lower() or
                any(query_lower in tag.lower() for tag in document["tags"])):
                results.append(document)
        
        return results
    
    def get_documents_by_category(self, category_id):
        """根据分类获取文档"""
        return [d for d in self.documents if d["category_id"] == category_id]
    
    def get_documents_by_tag(self, tag):
        """根据标签获取文档"""
        return [d for d in self.documents if tag in d["tags"]]
    
    def create_category(self, category_data):
        """创建分类"""
        # 生成唯一ID
        category_id = f"cat_{int(time.time())}"
        
        # 创建分类对象
        category = {
            "id": category_id,
            "name": category_data.get("name", "新分类"),
            "description": category_data.get("description", ""),
            "parent_id": category_data.get("parent_id", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到分类列表
        self.categories.append(category)
        self._save_categories()
        
        return category
    
    def get_categories(self):
        """获取所有分类"""
        return self.categories
    
    def get_category(self, category_id):
        """获取指定分类"""
        return next((c for c in self.categories if c["id"] == category_id), None)
    
    def update_category(self, category_id, category_data):
        """更新分类"""
        for i, category in enumerate(self.categories):
            if category["id"] == category_id:
                # 更新分类数据
                self.categories[i].update(category_data)
                self.categories[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_categories()
                return self.categories[i]
        return None
    
    def delete_category(self, category_id):
        """删除分类"""
        # 先更新该分类下的文档，将其分类ID设为空
        for i, document in enumerate(self.documents):
            if document["category_id"] == category_id:
                self.documents[i]["category_id"] = ""
        
        # 删除分类
        self.categories = [c for c in self.categories if c["id"] != category_id]
        self._save_categories()
        self._save_documents()
        return True
    
    def create_tag(self, tag_data):
        """创建标签"""
        # 检查标签是否已存在
        existing_tag = next((t for t in self.tags if t["name"].lower() == tag_data["name"].lower()), None)
        if existing_tag:
            return existing_tag
        
        # 生成唯一ID
        tag_id = f"tag_{int(time.time())}"
        
        # 创建标签对象
        tag = {
            "id": tag_id,
            "name": tag_data.get("name", "新标签"),
            "description": tag_data.get("description", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到标签列表
        self.tags.append(tag)
        self._save_tags()
        
        return tag
    
    def get_tags(self):
        """获取所有标签"""
        return self.tags
    
    def get_tag(self, tag_id):
        """获取指定标签"""
        return next((t for t in self.tags if t["id"] == tag_id), None)
    
    def update_tag(self, tag_id, tag_data):
        """更新标签"""
        for i, tag in enumerate(self.tags):
            if tag["id"] == tag_id:
                # 更新标签数据
                self.tags[i].update(tag_data)
                self.tags[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_tags()
                return self.tags[i]
        return None
    
    def delete_tag(self, tag_id):
        """删除标签"""
        # 获取标签名称
        tag = self.get_tag(tag_id)
        if not tag:
            return False
        
        # 从所有文档中移除该标签
        for i, document in enumerate(self.documents):
            if tag["name"] in document["tags"]:
                self.documents[i]["tags"].remove(tag["name"])
        
        # 删除标签
        self.tags = [t for t in self.tags if t["id"] != tag_id]
        self._save_tags()
        self._save_documents()
        return True
    
    def add_view(self, document_id):
        """增加文档浏览量"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                self.documents[i]["views"] += 1
                self._save_documents()
                return self.documents[i]
        return None
    
    def toggle_like(self, document_id):
        """切换文档点赞状态"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                self.documents[i]["likes"] += 1
                self._save_documents()
                return self.documents[i]
        return None
    
    def _load_document_versions(self):
        """加载文档版本数据"""
        versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        if os.path.exists(versions_file):
            with open(versions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_document_versions(self):
        """保存文档版本数据"""
        versions_file = os.path.join(self.knowledge_dir, "document_versions.json")
        with open(versions_file, "w", encoding="utf-8") as f:
            json.dump(self.document_versions, f, ensure_ascii=False, indent=2)
    
    def _load_permissions(self):
        """加载权限数据"""
        if os.path.exists(self.permissions_file):
            with open(self.permissions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_permissions(self):
        """保存权限数据"""
        with open(self.permissions_file, "w", encoding="utf-8") as f:
            json.dump(self.permissions, f, ensure_ascii=False, indent=2)
    
    def save_document_version(self, document):
        """保存文档版本"""
        """
        保存文档的当前版本到历史记录中
        
        Args:
            document (dict): 文档对象
        """
        # 创建版本记录
        version_record = {
            "id": f"version_{int(time.time())}",
            "document_id": document["id"],
            "version": document.get("version", 1),
            "title": document["title"],
            "content": document["content"],
            "author": document.get("author", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": document.get("file_path", ""),
            "file_name": document.get("file_name", ""),
            "file_type": document.get("file_type", "")
        }
        
        # 添加到版本记录
        self.document_versions.append(version_record)
        self._save_document_versions()
    
    def update_document(self, document_id, document_data):
        """更新文档（带版本控制）"""
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 保存当前版本
                self.save_document_version(document)
                
                # 更新文档数据
                self.documents[i].update(document_data)
                
                # 增加版本号
                if "content" in document_data or "file_path" in document_data:
                    self.documents[i]["version"] = self.documents[i].get("version", 1) + 1
                
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_documents()
                return self.documents[i]
        return None
    
    def get_document_versions(self, document_id):
        """获取文档的所有版本"""
        """
        获取指定文档的所有历史版本
        
        Args:
            document_id (str): 文档ID
        
        Returns:
            list: 文档版本列表
        """
        versions = [v for v in self.document_versions if v["document_id"] == document_id]
        # 按版本号降序排序
        versions.sort(key=lambda x: x["version"], reverse=True)
        return versions
    
    def get_document_version(self, version_id):
        """获取指定版本"""
        """
        获取文档的指定版本
        
        Args:
            version_id (str): 版本ID
        
        Returns:
            dict: 版本信息
        """
        return next((v for v in self.document_versions if v["id"] == version_id), None)
    
    def restore_document_version(self, document_id, version_id):
        """恢复文档到指定版本"""
        """
        将文档恢复到指定的历史版本
        
        Args:
            document_id (str): 文档ID
            version_id (str): 要恢复的版本ID
        
        Returns:
            dict: 更新后的文档信息
        """
        # 获取指定版本
        version = self.get_document_version(version_id)
        if not version:
            return None
        
        # 获取当前文档
        for i, document in enumerate(self.documents):
            if document["id"] == document_id:
                # 保存当前版本（作为新版本）
                self.save_document_version(document)
                
                # 恢复到指定版本
                self.documents[i]["title"] = version["title"]
                self.documents[i]["content"] = version["content"]
                self.documents[i]["file_path"] = version["file_path"]
                self.documents[i]["file_name"] = version["file_name"]
                self.documents[i]["file_type"] = version["file_type"]
                
                # 增加版本号
                self.documents[i]["version"] += 1
                self.documents[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self._save_documents()
                return self.documents[i]
        return None
    
    def add_document_permission(self, permission_data):
        """添加文档权限"""
        """
        为文档添加权限
        
        Args:
            permission_data (dict): 权限信息，包含document_id, user_id, role, permissions等字段
        
        Returns:
            dict: 添加的权限信息
        """
        # 生成权限ID
        permission_id = f"permission_{int(time.time())}"
        
        # 创建权限对象
        permission = {
            "id": permission_id,
            "document_id": permission_data["document_id"],
            "user_id": permission_data.get("user_id", ""),
            "role": permission_data.get("role", "reader"),  # reader, editor, admin
            "permissions": permission_data.get("permissions", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到权限列表
        self.permissions.append(permission)
        self._save_permissions()
        
        return permission
    
    def get_document_permissions(self, document_id):
        """获取文档的所有权限"""
        """
        获取指定文档的所有权限
        
        Args:
            document_id (str): 文档ID
        
        Returns:
            list: 权限列表
        """
        return [p for p in self.permissions if p["document_id"] == document_id]
    
    def check_document_permission(self, document_id, user_id, permission_type):
        """检查用户是否有指定权限"""
        """
        检查用户是否对文档有指定类型的权限
        
        Args:
            document_id (str): 文档ID
            user_id (str): 用户ID
            permission_type (str): 权限类型，如'read', 'edit', 'delete', 'manage'
        
        Returns:
            bool: 是否有该权限
        """
        # 获取文档权限
        document_permissions = self.get_document_permissions(document_id)
        
        # 检查用户权限
        for perm in document_permissions:
            if perm["user_id"] == user_id:
                # 角色权限映射
                role_permissions = {
                    "reader": ["read"],
                    "editor": ["read", "edit"],
                    "admin": ["read", "edit", "delete", "manage"]
                }
                
                # 检查角色权限
                if permission_type in role_permissions.get(perm["role"], []):
                    return True
                
                # 检查具体权限
                if permission_type in perm.get("permissions", []):
                    return True
        
        # 默认权限：文档作者有所有权限
        document = self.get_document(document_id)
        if document and document.get("author") == user_id:
            return True
        
        # 默认权限：公开文档允许只读访问
        document = self.get_document(document_id)
        if document and document.get("status") == "published":
            if permission_type == "read":
                return True
        
        return False
    
    def update_document_permission(self, permission_id, permission_data):
        """更新文档权限"""
        """
        更新指定的文档权限
        
        Args:
            permission_id (str): 权限ID
            permission_data (dict): 更新的权限数据
        
        Returns:
            dict: 更新后的权限信息
        """
        for i, permission in enumerate(self.permissions):
            if permission["id"] == permission_id:
                self.permissions[i].update(permission_data)
                self.permissions[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_permissions()
                return self.permissions[i]
        return None
    
    def delete_document_permission(self, permission_id):
        """删除文档权限"""
        """
        删除指定的文档权限
        
        Args:
            permission_id (str): 权限ID
        
        Returns:
            bool: 删除是否成功
        """
        self.permissions = [p for p in self.permissions if p["id"] != permission_id]
        self._save_permissions()
        return True
    
    def get_document_statistics(self):
        """获取文档统计信息"""
        """
        获取知识库的统计信息
        
        Returns:
            dict: 统计信息
        """
        total_documents = len(self.documents)
        published_documents = len([d for d in self.documents if d["status"] == "published"])
        draft_documents = len([d for d in self.documents if d["status"] == "draft"])
        archived_documents = len([d for d in self.documents if d["status"] == "archived"])
        
        total_categories = len(self.categories)
        total_tags = len(self.tags)
        total_versions = len(self.document_versions)
        
        # 计算总浏览量和点赞数
        total_views = sum(d.get("views", 0) for d in self.documents)
        total_likes = sum(d.get("likes", 0) for d in self.documents)
        
        return {
            "total_documents": total_documents,
            "published_documents": published_documents,
            "draft_documents": draft_documents,
            "archived_documents": archived_documents,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "total_versions": total_versions,
            "total_views": total_views,
            "total_likes": total_likes
        }
    
    # RAG库管理方法
    def _load_rag_libraries(self):
        """加载RAG库数据"""
        if os.path.exists(self.rag_libraries_file):
            with open(self.rag_libraries_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_rag_libraries(self):
        """保存RAG库数据"""
        with open(self.rag_libraries_file, "w", encoding="utf-8") as f:
            json.dump(self.rag_libraries, f, ensure_ascii=False, indent=2)
    
    def create_rag_library(self, library_data):
        """创建RAG库"""
        # 生成唯一ID
        library_id = f"raglib_{int(time.time())}"
        
        # 创建RAG库对象
        library = {
            "id": library_id,
            "name": library_data.get("name", "新建RAG库"),
            "description": library_data.get("description", ""),
            "documents": library_data.get("documents", []),
            "author": library_data.get("author", ""),
            "visibility": library_data.get("visibility", "private"),  # private, team, public
            "embedding_model": library_data.get("embedding_model", "all-MiniLM-L6-v2"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usage_count": 0
        }
        
        # 添加到RAG库列表
        self.rag_libraries.append(library)
        self._save_rag_libraries()
        
        return library
    
    def get_rag_libraries(self):
        """获取所有RAG库"""
        return self.rag_libraries
    
    def get_rag_library(self, library_id):
        """获取指定RAG库"""
        return next((lib for lib in self.rag_libraries if lib["id"] == library_id), None)
    
    def update_rag_library(self, library_id, library_data):
        """更新RAG库"""
        for i, library in enumerate(self.rag_libraries):
            if library["id"] == library_id:
                # 更新RAG库数据
                self.rag_libraries[i].update(library_data)
                self.rag_libraries[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_rag_libraries()
                return self.rag_libraries[i]
        return None
    
    def delete_rag_library(self, library_id):
        """删除RAG库"""
        self.rag_libraries = [lib for lib in self.rag_libraries if lib["id"] != library_id]
        self._save_rag_libraries()
        return True
    
    def add_document_to_rag_library(self, library_id, document_id):
        """添加文档到RAG库"""
        library = self.get_rag_library(library_id)
        if library and document_id not in library["documents"]:
            library["documents"].append(document_id)
            library["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_rag_libraries()
            # 生成并保存文档嵌入
            self.generate_embedding(document_id, library_id)
            return True
        return False
    
    def remove_document_from_rag_library(self, library_id, document_id):
        """从RAG库移除文档"""
        library = self.get_rag_library(library_id)
        if library and document_id in library["documents"]:
            library["documents"].remove(document_id)
            library["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_rag_libraries()
            # 删除文档嵌入
            embedding_file = os.path.join(self.rag_embeddings_dir, f"{library_id}_{document_id}.json")
            if os.path.exists(embedding_file):
                os.remove(embedding_file)
            return True
        return False
    
    def get_rag_library_documents(self, library_id):
        """获取RAG库中的文档"""
        library = self.get_rag_library(library_id)
        if not library:
            return []
        
        documents = []
        for document_id in library["documents"]:
            document = self.get_document(document_id)
            if document:
                documents.append(document)
        return documents
    
    def generate_embedding(self, document_id, library_id):
        """生成文档嵌入"""
        document = self.get_document(document_id)
        if not document:
            return None
        
        # 生成嵌入
        text = document["title"] + " " + document["content"]
        embedding = self.embedding_model.encode(text).tolist()
        
        # 保存嵌入
        embedding_data = {
            "document_id": document_id,
            "library_id": library_id,
            "embedding": embedding,
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        embedding_file = os.path.join(self.rag_embeddings_dir, f"{library_id}_{document_id}.json")
        with open(embedding_file, "w", encoding="utf-8") as f:
            json.dump(embedding_data, f, ensure_ascii=False, indent=2)
        
        return embedding_data
    
    def load_embedding(self, library_id, document_id):
        """加载文档嵌入"""
        embedding_file = os.path.join(self.rag_embeddings_dir, f"{library_id}_{document_id}.json")
        if os.path.exists(embedding_file):
            with open(embedding_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def generate_all_embeddings(self, library_id):
        """生成RAG库中所有文档的嵌入"""
        library = self.get_rag_library(library_id)
        if not library:
            return False
        
        for document_id in library["documents"]:
            self.generate_embedding(document_id, library_id)
        
        return True
    
    def rag_query(self, query, library_id, top_k=5):
        """执行RAG查询"""
        library = self.get_rag_library(library_id)
        if not library:
            return []
        
        # 生成查询嵌入
        query_embedding = self.embedding_model.encode(query).reshape(1, -1)
        
        # 加载所有文档嵌入
        embeddings = []
        document_ids = []
        
        for document_id in library["documents"]:
            embedding_data = self.load_embedding(library_id, document_id)
            if embedding_data:
                embeddings.append(embedding_data["embedding"])
                document_ids.append(document_id)
        
        if not embeddings:
            return []
        
        # 计算相似度
        embeddings_np = np.array(embeddings)
        similarities = cosine_similarity(query_embedding, embeddings_np)[0]
        
        # 获取相似度最高的top_k个文档
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 准备结果
        results = []
        for i in top_indices:
            document_id = document_ids[i]
            document = self.get_document(document_id)
            if document:
                results.append({
                    "document": document,
                    "similarity": float(similarities[i]),
                    "text": document["content"][:500] + ("..." if len(document["content"]) > 500 else "")
                })
        
        # 更新RAG库使用次数
        library["usage_count"] += 1
        self._save_rag_libraries()
        
        return results
    
    def batch_rag_query(self, queries, library_id, top_k=3):
        """批量执行RAG查询"""
        results = []
        for query in queries:
            results.append(self.rag_query(query, library_id, top_k))
        return results
    
    def get_rag_library_statistics(self, library_id):
        """获取RAG库统计信息"""
        library = self.get_rag_library(library_id)
        if not library:
            return None
        
        return {
            "id": library["id"],
            "name": library["name"],
            "document_count": len(library["documents"]),
            "usage_count": library["usage_count"],
            "created_at": library["created_at"],
            "updated_at": library["updated_at"]
        }
    
    def search_rag_libraries(self, query):
        """搜索RAG库"""
        results = []
        query_lower = query.lower()
        
        for library in self.rag_libraries:
            if (query_lower in library["name"].lower() or 
                query_lower in library["description"].lower()):
                results.append(library)
        
        return results
