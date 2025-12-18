import os
import tempfile
import shutil
from datetime import datetime
from .document_converter import DocumentConverter
from .kroki_renderer import KrokiRenderer
from .ascii_image_converter import ASCIIImageConverter

class BatchProcessor:
    """
    批量处理器，用于批量处理文档转换任务
    """
    
    def __init__(self):
        self.document_converter = DocumentConverter()
        self.kroki_renderer = KrokiRenderer()
        self.ascii_converter = ASCIIImageConverter()
        self.processing = False
        self.current_progress = 0
        self.total_tasks = 0
        self.current_task = 0
        self.current_task_info = ""
    
    def process_batch(self, input_files, conversion_config):
        """
        批量处理文件转换
        
        Args:
            input_files: 输入文件列表
            conversion_config: 转换配置
            
        Returns:
            dict: 批量处理结果
        """
        try:
            if self.processing:
                return {
                    'success': False,
                    'message': '已有批量处理任务正在进行中'
                }
            
            # 初始化处理状态
            self.processing = True
            self.current_progress = 0
            self.total_tasks = len(input_files)
            self.current_task = 0
            self.current_task_info = ""
            
            # 验证转换配置
            if not conversion_config or 'output_format' not in conversion_config:
                return {
                    'success': False,
                    'message': '转换配置不完整，缺少output_format'
                }
            
            output_format = conversion_config['output_format']
            output_dir = conversion_config.get('output_dir', os.getcwd())
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            for i, input_file in enumerate(input_files):
                self.current_task = i + 1
                self.current_task_info = f"处理文件 {os.path.basename(input_file)}"
                self.current_progress = int((i / self.total_tasks) * 100)
                
                if not os.path.exists(input_file):
                    results.append({
                        'file': input_file,
                        'success': False,
                        'message': '文件不存在'
                    })
                    continue
                
                # 根据文件类型选择处理方式
                file_ext = os.path.splitext(input_file)[1].lower()[1:]
                
                # 处理包含图表的文档
                if conversion_config.get('process_charts', False):
                    # 读取文件内容
                    with open(input_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 渲染图表
                    chart_output_dir = os.path.join(output_dir, 'charts')
                    os.makedirs(chart_output_dir, exist_ok=True)
                    
                    chart_result = self.kroki_renderer.render_text_with_charts(
                        content,
                        chart_output_dir,
                        conversion_config.get('chart_format', 'svg')
                    )
                    
                    if chart_result['success']:
                        content = chart_result['text']
                    
                # 处理ASCII图像
                if conversion_config.get('process_ascii', False):
                    # 读取文件内容（如果之前没读取的话）
                    if 'content' not in locals():
                        with open(input_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # 转换ASCII图像
                    ascii_output_dir = os.path.join(output_dir, 'ascii_images')
                    os.makedirs(ascii_output_dir, exist_ok=True)
                    
                    ascii_result = self.ascii_converter.convert_text_with_ascii(
                        content,
                        ascii_output_dir,
                        conversion_config.get('ascii_options', {})
                    )
                    
                    if ascii_result['success']:
                        content = ascii_result['text']
                
                # 执行文档转换
                if 'content' in locals():
                    # 使用处理后的内容进行转换
                    result = self.document_converter.convert(
                        content,
                        file_ext,
                        output_format,
                        conversion_config.get('conversion_options', [])
                    )
                    
                    if result['success']:
                        # 保存转换结果
                        base_name = os.path.splitext(os.path.basename(input_file))[0]
                        output_path = os.path.join(output_dir, f'{base_name}.{output_format}')
                        
                        if 'content' in result:
                            # 文本格式，直接写入文件
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write(result['content'])
                        else:
                            # 二进制格式，移动文件
                            os.rename(result['file_path'], output_path)
                            # 清理临时输入文件
                            if 'input_file' in result:
                                os.unlink(result['input_file'])
                        
                        result['file_path'] = output_path
                else:
                    # 直接转换文件
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    output_path = os.path.join(output_dir, f'{base_name}.{output_format}')
                    result = self.document_converter.convert_file(
                        input_file,
                        output_path,
                        conversion_config.get('conversion_options', [])
                    )
                
                result['file'] = input_file
                results.append(result)
                
                # 更新进度
                self.current_progress = int(((i + 1) / self.total_tasks) * 100)
            
            # 完成处理
            self.processing = False
            self.current_progress = 100
            self.current_task_info = "批量处理完成"
            
            return {
                'success': True,
                'results': results,
                'total_tasks': self.total_tasks,
                'successful_tasks': sum(1 for r in results if r['success']),
                'message': '批量处理完成，共处理 {total} 个文件，成功 {success} 个'.format(total=self.total_tasks, success=sum(1 for r in results if r['success']))
            }
        except Exception as e:
            self.processing = False
            return {
                'success': False,
                'message': '批量处理失败：' + str(e)
            }
    
    def process_text_batch(self, texts, conversion_config):
        """
        批量处理文本内容转换
        
        Args:
            texts: 文本内容列表，每个元素是包含id和content的字典
            conversion_config: 转换配置
            
        Returns:
            dict: 批量处理结果
        """
        try:
            if self.processing:
                return {
                    'success': False,
                    'message': '已有批量处理任务正在进行中'
                }
            
            # 初始化处理状态
            self.processing = True
            self.current_progress = 0
            self.total_tasks = len(texts)
            self.current_task = 0
            self.current_task_info = ""
            
            # 验证转换配置
            if not conversion_config or 'output_format' not in conversion_config:
                return {
                    'success': False,
                    'message': '转换配置不完整，缺少output_format'
                }
            
            output_format = conversion_config['output_format']
            output_dir = conversion_config.get('output_dir', os.getcwd())
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            for i, text_item in enumerate(texts):
                self.current_task = i + 1
                self.current_task_info = f"处理文本 {text_item.get('id', i+1)}"
                self.current_progress = int((i / self.total_tasks) * 100)
                
                content = text_item.get('content', '')
                text_id = text_item.get('id', f'text_{i+1}')
                input_format = text_item.get('format', 'markdown')
                
                if not content:
                    results.append({
                        'id': text_id,
                        'success': False,
                        'message': '文本内容为空'
                    })
                    continue
                
                # 处理包含图表的文档
                if conversion_config.get('process_charts', False):
                    # 渲染图表
                    chart_output_dir = os.path.join(output_dir, 'charts')
                    os.makedirs(chart_output_dir, exist_ok=True)
                    
                    chart_result = self.kroki_renderer.render_text_with_charts(
                        content,
                        chart_output_dir,
                        conversion_config.get('chart_format', 'svg')
                    )
                    
                    if chart_result['success']:
                        content = chart_result['text']
                
                # 处理ASCII图像
                if conversion_config.get('process_ascii', False):
                    # 转换ASCII图像
                    ascii_output_dir = os.path.join(output_dir, 'ascii_images')
                    os.makedirs(ascii_output_dir, exist_ok=True)
                    
                    ascii_result = self.ascii_converter.convert_text_with_ascii(
                        content,
                        ascii_output_dir,
                        conversion_config.get('ascii_options', {})
                    )
                    
                    if ascii_result['success']:
                        content = ascii_result['text']
                
                # 执行文档转换
                result = self.document_converter.convert(
                    content,
                    input_format,
                    output_format,
                    conversion_config.get('conversion_options', [])
                )
                
                if result['success']:
                    # 保存转换结果
                    output_path = os.path.join(output_dir, f'{text_id}.{output_format}')
                    
                    if 'content' in result:
                        # 文本格式，直接写入文件
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(result['content'])
                    else:
                        # 二进制格式，移动文件
                        os.rename(result['file_path'], output_path)
                        # 清理临时输入文件
                        if 'input_file' in result:
                            os.unlink(result['input_file'])
                    
                    result['file_path'] = output_path
                
                result['id'] = text_id
                results.append(result)
                
                # 更新进度
                self.current_progress = int(((i + 1) / self.total_tasks) * 100)
            
            # 完成处理
            self.processing = False
            self.current_progress = 100
            self.current_task_info = "批量处理完成"
            
            success_count = sum(1 for r in results if r['success'])
            message = '批量处理完成，共处理 {total} 个文本，成功 {success} 个'.format(total=self.total_tasks, success=success_count)
            return {
                'success': True,
                'results': results,
                'total_tasks': self.total_tasks,
                'successful_tasks': success_count,
                'message': message
            }
        except Exception as e:
            self.processing = False
            return {
                'success': False,
                'message': '批量处理失败：' + str(e)
            }
    
    def get_progress(self):
        """
        获取处理进度
        
        Returns:
            dict: 进度信息
        """
        return {
            'processing': self.processing,
            'current_progress': self.current_progress,
            'total_tasks': self.total_tasks,
            'current_task': self.current_task,
            'current_task_info': self.current_task_info
        }
    
    def cancel_processing(self):
        """
        取消正在进行的批量处理
        
        Returns:
            dict: 取消结果
        """
        if not self.processing:
            return {
                'success': False,
                'message': '没有正在进行的批量处理任务'
            }
        
        # 这里可以添加实际的取消逻辑
        # 目前只是简单地标记为未处理
        self.processing = False
        self.current_progress = 0
        self.total_tasks = 0
        self.current_task = 0
        self.current_task_info = "处理已取消"
        
        return {
            'success': True,
            'message': '批量处理已取消'
        }
    
    def get_supported_formats(self):
        """
        获取支持的转换格式
        
        Returns:
            list: 支持的格式列表
        """
        return self.document_converter.get_supported_formats()