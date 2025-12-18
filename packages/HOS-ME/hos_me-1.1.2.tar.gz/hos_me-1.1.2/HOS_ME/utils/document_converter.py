import os
import subprocess
import tempfile
import json
from datetime import datetime

# 导入其他转换工具
from .kroki_renderer import KrokiRenderer
from .ascii_image_converter import ASCIIImageConverter

class DocumentConverter:
    """
    文档转换引擎，封装Pandoc的核心功能，支持多种格式间的转换
    集成了Kroki图表渲染和ASCII图像转换功能
    """
    
    def __init__(self):
        self.supported_formats = [
            'markdown', 'html', 'docx', 'pdf', 'latex', 'epub', 'txt',
            'md', 'rst', 'org', 'json', 'xml', 'odt', 'rtf'
        ]
        self.pandoc_path = self._find_pandoc()
        # 初始化集成的转换工具
        self.kroki_renderer = KrokiRenderer()
        self.ascii_converter = ASCIIImageConverter()
        # 支持的Pandoc扩展
        self.supported_extensions = [
            'table_captions', 'multiline_tables', 'grid_tables', 'pipe_tables',
            'fenced_code_blocks', 'fenced_code_attributes', 'backtick_code_blocks',
            'definition_lists', 'footnotes', 'inline_notes', 'citations',
            'raw_html', 'raw_tex', 'tex_math_dollars', 'tex_math_double_backslash',
            'latex_macros', 'auto_identifiers', 'header_attributes',
            'implicit_header_references', 'footnotes', 'citations'
        ]
    
    def _find_pandoc(self):
        """
        查找系统中的Pandoc可执行文件路径
        """
        try:
            # 尝试直接调用pandoc命令
            result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'pandoc'
        except FileNotFoundError:
            pass
        
        # 尝试在常见路径中查找
        common_paths = [
            '/usr/local/bin/pandoc',
            '/usr/bin/pandoc',
            'C:\Program Files\Pandoc\pandoc.exe',
            'C:\Program Files (x86)\Pandoc\pandoc.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self):
        """
        检查Pandoc是否可用
        """
        return self.pandoc_path is not None
    
    def convert(self, input_content, from_format, to_format, options=None):
        """
        转换文档内容
        
        Args:
            input_content: 输入文档内容
            from_format: 输入格式
            to_format: 输出格式
            options: 额外的转换选项，支持以下特殊选项：
                - preprocess_charts: 是否预处理图表（默认True）
                - preprocess_ascii: 是否预处理ASCII图像（默认True）
                - chart_format: 图表输出格式（默认svg）
                - ascii_image_options: ASCII图像转换选项
                - pandoc_extensions: Pandoc扩展列表
                - pandoc_args: 额外的Pandoc命令行参数
            
        Returns:
            dict: 转换结果，包含success、content/file_path、message等
        """
        if not self.is_available():
            return {
                'success': False,
                'message': 'Pandoc未安装或不可用'
            }
        
        # 验证格式
        if from_format not in self.supported_formats or to_format not in self.supported_formats:
            return {
                'success': False,
                'message': '不支持的格式。支持的格式：' + ', '.join(self.supported_formats)
            }
        
        # 设置默认选项
        default_options = {
            'preprocess_charts': True,
            'preprocess_ascii': True,
            'chart_format': 'svg',
            'ascii_image_options': None,
            'pandoc_extensions': [],
            'pandoc_args': []
        }
        
        if options:
            default_options.update(options)
        
        options = default_options
        processed_content = input_content
        temp_files = []
        images_info = []
        charts_info = []
        
        try:
            # 创建临时工作目录
            temp_dir = tempfile.mkdtemp()
            temp_files.append(temp_dir)
            
            # 1. 预处理：处理文档中的图表
            if options['preprocess_charts']:
                chart_result = self.kroki_renderer.render_text_with_charts(
                    processed_content, 
                    temp_dir, 
                    output_format=options['chart_format'],
                    options=None
                )
                if chart_result['success']:
                    processed_content = chart_result['text']
                    charts_info = chart_result['charts']
            
            # 2. 预处理：处理文档中的ASCII图像
            if options['preprocess_ascii']:
                ascii_result = self.ascii_converter.convert_text_with_ascii(
                    processed_content, 
                    temp_dir, 
                    options=options['ascii_image_options']
                )
                if ascii_result['success']:
                    processed_content = ascii_result['text']
                    images_info.extend(ascii_result['images'])
            
            # 3. 执行Pandoc转换
            
            # 创建输入文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.' + from_format, delete=False) as f:
                f.write(processed_content)
                input_file = f.name
            temp_files.append(input_file)
            
            output_file = input_file + '.' + to_format
            temp_files.append(output_file)
            
            # 构建命令
            cmd = [self.pandoc_path, input_file, '-o', output_file]
            
            # 添加Pandoc扩展
            if options['pandoc_extensions']:
                # 验证扩展是否支持
                valid_extensions = [ext for ext in options['pandoc_extensions'] 
                                  if ext in self.supported_extensions]
                if valid_extensions:
                    from_format_with_extensions = from_format + '+' + ','.join(valid_extensions)
                    cmd.extend(['--from', from_format_with_extensions])
            
            # 添加额外的Pandoc参数
            if options['pandoc_args']:
                cmd.extend(options['pandoc_args'])
            
            # 添加用户指定的额外选项
            if isinstance(options.get('extra_args'), list):
                cmd.extend(options['extra_args'])
            
            # 执行转换
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # 读取输出内容
                if to_format in ['txt', 'markdown', 'html', 'latex', 'md', 'rst', 'org', 'json', 'xml']:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        output_content = f.read()
                    
                    return {
                        'success': True,
                        'content': output_content,
                        'message': '转换成功',
                        'charts_info': charts_info,
                        'images_info': images_info,
                        'temp_dir': temp_dir
                    }
                else:
                    # 对于二进制格式，返回文件路径
                    return {
                        'success': True,
                        'file_path': output_file,
                        'message': '转换成功',
                        'charts_info': charts_info,
                        'images_info': images_info,
                        'temp_dir': temp_dir
                    }
            else:
                return {
                    'success': False,
                    'message': '转换失败：' + result.stderr,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
        except Exception as e:
            return {
                'success': False,
                'message': '转换异常：' + str(e)
            }
        finally:
            # 清理临时文件（可选，由调用者决定是否保留）
            # 注意：如果返回了文件路径，不要清理，让调用者处理
            pass
    
    def convert_file(self, input_path, output_path, options=None):
        """
        转换文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            options: 额外的转换选项
            
        Returns:
            dict: 转换结果
        """
        if not self.is_available():
            return {
                'success': False,
                'message': 'Pandoc未安装或不可用'
            }
        
        # 提取格式
        from_format = os.path.splitext(input_path)[1][1:]
        to_format = os.path.splitext(output_path)[1][1:]
        
        # 验证格式
        if from_format not in self.supported_formats or to_format not in self.supported_formats:
            return {
                'success': False,
                'message': '不支持的格式。支持的格式：' + ', '.join(self.supported_formats)
            }
        
        # 读取输入文件内容
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                input_content = f.read()
        except Exception as e:
            return {
                'success': False,
                'message': '读取输入文件失败：' + str(e)
            }
        
        # 使用convert方法转换
        result = self.convert(input_content, from_format, to_format, options)
        
        if result['success'] and 'file_path' in result:
            # 移动输出文件到指定路径
            try:
                import shutil
                shutil.copy2(result['file_path'], output_path)
                # 清理临时文件
                if 'temp_dir' in result:
                    import shutil
                    shutil.rmtree(result['temp_dir'], ignore_errors=True)
                # 更新结果
                result['file_path'] = output_path
            except Exception as e:
                return {
                    'success': False,
                    'message': '保存输出文件失败：' + str(e)
                }
        
        return result
    
    def get_supported_formats(self):
        """
        获取支持的格式列表
        """
        return self.supported_formats
    
    def get_pandoc_version(self):
        """
        获取Pandoc版本信息
        """
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run([self.pandoc_path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split('\n')[0]
            return None
        except Exception:
            return None
    
    def get_supported_extensions(self):
        """
        获取支持的Pandoc扩展列表
        """
        return self.supported_extensions
    
    def batch_convert(self, input_files, output_dir, to_format, options=None):
        """
        批量转换文件
        
        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
            to_format: 输出格式
            options: 转换选项
            
        Returns:
            dict: 批量转换结果
        """
        results = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            if not os.path.exists(input_file):
                results.append({
                    'file': input_file,
                    'success': False,
                    'message': '文件不存在'
                })
                continue
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, base_name + '.' + to_format)
            
            # 转换文件
            result = self.convert_file(input_file, output_file, options)
            result['file'] = input_file
            results.append(result)
        
        return {
            'success': True,
            'results': results,
            'message': '批量转换完成，共处理 ' + str(len(input_files)) + ' 个文件'
        }
    
    def create_complex_table(self, data, headers, rowspan=None, colspan=None):
        """
        创建支持跨行跨列的复杂表格
        
        Args:
            data: 表格数据
            headers: 表头
            rowspan: 行跨度信息
            colspan: 列跨度信息
            
        Returns:
            str: HTML格式的复杂表格
        """
        # 生成HTML表格
        html = ['<table>']
        html.append('<thead>')
        html.append('<tr>')
        for header in headers:
            html.append('<th>' + header + '</th>')
        html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        
        for i, row in enumerate(data):
            html.append('<tr>')
            for j, cell in enumerate(row):
                # 检查是否有跨行列
                rowspan_attr = ''
                colspan_attr = ''
                if rowspan and rowspan[i][j] > 1:
                    rowspan_attr = ' rowspan="' + str(rowspan[i][j]) + '"'
                if colspan and colspan[i][j] > 1:
                    colspan_attr = ' colspan="' + str(colspan[i][j]) + '"'
                html.append('<td' + rowspan_attr + colspan_attr + '>' + str(cell) + '</td>')
            html.append('</tr>')
        
        html.append('</tbody>')
        html.append('</table>')
        
        return ''.join(html)
    
    def optimize_for_web(self, html_content, options=None):
        """
        优化HTML内容以适合Web发布
        
        Args:
            html_content: HTML内容
            options: 优化选项
            
        Returns:
            dict: 优化结果
        """
        # 基本优化：移除多余空白
        import re
        optimized = re.sub(r'\s+', ' ', html_content)
        optimized = re.sub(r'>\s+<', '><', optimized)
        
        return {
            'success': True,
            'content': optimized,
            'message': 'HTML优化完成'
        }