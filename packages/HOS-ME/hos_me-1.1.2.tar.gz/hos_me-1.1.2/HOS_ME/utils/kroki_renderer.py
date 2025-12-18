import os
import requests
import base64
import re
from datetime import datetime

class KrokiRenderer:
    """
    Kroki图表渲染器，用于免费渲染多种图表类型
    """
    
    def __init__(self):
        self.kroki_api_url = "https://kroki.io"
        self.supported_diagrams = [
            'mermaid', 'plantuml', 'graphviz', 'ditaa', 'svgbob', 
            'umlet', 'vega', 'vegalite', 'wavedrom', 'blockdiag',
            'seqdiag', 'actdiag', 'nwdiag', 'packetdiag', 'rackdiag'
        ]
        self.supported_output_formats = ['svg', 'png', 'jpeg', 'pdf']
    
    def render_chart(self, diagram_type, chart_code, output_format='svg', options=None):
        """
        渲染图表
        
        Args:
            diagram_type: 图表类型
            chart_code: 图表代码
            output_format: 输出格式
            options: 额外选项
            
        Returns:
            dict: 渲染结果
        """
        try:
            # 验证图表类型
            if diagram_type not in self.supported_diagrams:
                return {
                    'success': False,
                    'message': '不支持的图表类型：' + diagram_type + '。支持的类型：' + ', '.join(self.supported_diagrams)
                }
            
            # 验证输出格式
            if output_format not in self.supported_output_formats:
                return {
                    'success': False,
                    'message': '不支持的输出格式：' + output_format + '。支持的格式：' + ', '.join(self.supported_output_formats)
                }
            
            # 清理图表代码
            chart_code = chart_code.strip()
            if not chart_code:
                return {
                    'success': False,
                    'message': '图表代码为空'
                }
            
            # 构建Kroki API URL
            encoded_code = base64.urlsafe_b64encode(chart_code.encode('utf-8')).decode('utf-8')
            url = f"{self.kroki_api_url}/{diagram_type}/{output_format}/{encoded_code}"
            
            # 发送请求
            headers = {'Accept': f'image/{output_format}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # 生成临时文件名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                temp_file = f"{diagram_type}_chart_{timestamp}.{output_format}"
                temp_path = os.path.join(tempfile.gettempdir(), temp_file)
                
                # 保存图表
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    'success': True,
                    'file_path': temp_path,
                    'content_type': response.headers.get('content-type'),
                    'message': f'{diagram_type}图表渲染成功'
                }
            else:
                return {
                    'success': False,
                    'message': f'图表渲染失败：Kroki API返回状态码 {response.status_code}，响应：{response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'图表渲染异常：{str(e)}'
            }
    
    def detect_chart_blocks(self, text_content):
        """
        检测文本中的图表代码块
        
        Args:
            text_content: 包含可能包含图表代码块的文本
            
        Returns:
            list: 检测到的图表代码块列表
        """
        chart_blocks = []
        
        # 正则表达式匹配图表代码块
        # 支持 ```diagram_type 和 ~~~diagram_type 格式
        pattern = r'```(\w+)\s*\n([\s\S]*?)\n```|~~~(\w+)\s*\n([\s\S]*?)\n~~~'
        matches = re.finditer(pattern, text_content, re.MULTILINE)
        
        for match in matches:
            if match.group(1):
                # ```diagram_type 格式
                diagram_type = match.group(1).lower()
                chart_code = match.group(2)
            else:
                # ~~~diagram_type 格式
                diagram_type = match.group(3).lower()
                chart_code = match.group(4)
            
            # 只匹配支持的图表类型
            if diagram_type in self.supported_diagrams:
                chart_blocks.append({
                    'diagram_type': diagram_type,
                    'chart_code': chart_code,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return chart_blocks
    
    def render_text_with_charts(self, text_content, output_dir, output_format='svg', options=None):
        """
        渲染文本中的图表代码块为真实图像，并返回替换后的文本
        
        Args:
            text_content: 包含图表代码块的文本
            output_dir: 输出图像目录
            output_format: 输出图像格式
            options: 额外选项
            
        Returns:
            dict: 渲染结果
        """
        try:
            # 检测图表代码块
            chart_blocks = self.detect_chart_blocks(text_content)
            if not chart_blocks:
                return {
                    'success': True,
                    'text': text_content,
                    'charts': [],
                    'message': '未检测到图表代码块'
                }
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 替换图表代码块
            replaced_text = []
            charts_info = []
            last_end_pos = 0
            
            for i, chart_block in enumerate(chart_blocks):
                # 添加图表代码块之前的内容
                if chart_block['start_pos'] > last_end_pos:
                    replaced_text.append(text_content[last_end_pos:chart_block['start_pos']])
                
                # 渲染图表
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                chart_name = '{diagram_type}_chart_{timestamp}_{i}.{output_format}'.format(diagram_type=chart_block['diagram_type'], timestamp=timestamp, i=i, output_format=output_format)
                chart_path = os.path.join(output_dir, chart_name)
                
                result = self.render_chart(
                    chart_block['diagram_type'],
                    chart_block['chart_code'],
                    output_format,
                    options
                )
                
                if result['success']:
                    # 移动图表到输出目录
                    os.rename(result['file_path'], chart_path)
                    
                    # 添加图像引用
                    replaced_text.append('![{diagram_type}图表 {i+1}]({chart_path})'.format(diagram_type=chart_block['diagram_type'], i=i, chart_path=chart_path))
                    charts_info.append({
                        'diagram_type': chart_block['diagram_type'],
                        'original_code': chart_block['chart_code'],
                        'image_path': chart_path
                    })
                else:
                    # 渲染失败，保留原始代码块
                    replaced_text.append(text_content[chart_block['start_pos']:chart_block['end_pos']])
                
                last_end_pos = chart_block['end_pos']
            
            # 添加剩余内容
            if last_end_pos < len(text_content):
                replaced_text.append(text_content[last_end_pos:])
            
            return {
                'success': True,
                'text': ''.join(replaced_text),
                'charts': charts_info,
                'message': f'成功渲染 {len(charts_info)} 个图表'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'渲染失败：{str(e)}'
            }
    
    def batch_render_charts(self, chart_files, output_dir, output_format='svg', options=None):
        """
        批量渲染图表文件
        
        Args:
            chart_files: 图表文件列表，每个文件包含一个图表代码块
            output_dir: 输出目录
            output_format: 输出格式
            options: 额外选项
            
        Returns:
            dict: 批量渲染结果
        """
        try:
            results = []
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            for chart_file in chart_files:
                if not os.path.exists(chart_file):
                    results.append({
                        'file': chart_file,
                        'success': False,
                        'message': '文件不存在'
                    })
                    continue
                
                # 读取文件内容
                with open(chart_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测图表代码块
                chart_blocks = self.detect_chart_blocks(content)
                
                if not chart_blocks:
                    # 如果没有检测到代码块，尝试直接渲染整个文件内容为mermaid图表
                    result = self.render_chart('mermaid', content, output_format, options)
                    if result['success']:
                        # 生成输出文件名
                        base_name = os.path.splitext(os.path.basename(chart_file))[0]
                        output_path = os.path.join(output_dir, f'{base_name}.{output_format}')
                        os.rename(result['file_path'], output_path)
                        result['file_path'] = output_path
                    result['file'] = chart_file
                    results.append(result)
                else:
                    # 渲染每个检测到的图表代码块
                    for i, chart_block in enumerate(chart_blocks):
                        result = self.render_chart(
                            chart_block['diagram_type'],
                            chart_block['chart_code'],
                            output_format,
                            options
                        )
                        if result['success']:
                            # 生成输出文件名
                            base_name = os.path.splitext(os.path.basename(chart_file))[0]
                            output_path = os.path.join(output_dir, f'{base_name}_{i}.{output_format}')
                            os.rename(result['file_path'], output_path)
                            result['file_path'] = output_path
                        result['file'] = chart_file
                        result['chart_index'] = i
                        results.append(result)
            
            return {
                'success': True,
                'results': results,
                'message': f'批量渲染完成，共处理 {len(chart_files)} 个文件'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'批量渲染失败：{str(e)}'
            }
    
    def get_supported_diagrams(self):
        """
        获取支持的图表类型
        """
        return self.supported_diagrams
    
    def get_supported_output_formats(self):
        """
        获取支持的输出格式
        """
        return self.supported_output_formats
    
    def set_kroki_api_url(self, url):
        """
        设置自定义Kroki API URL
        """
        self.kroki_api_url = url