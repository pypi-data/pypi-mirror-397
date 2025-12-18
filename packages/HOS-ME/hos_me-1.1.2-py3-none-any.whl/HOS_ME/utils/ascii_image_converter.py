import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import re
from datetime import datetime

class ASCIIImageConverter:
    """
    ASCII图像转换器，支持将ASCII伪图像转换为真实图像
    """
    
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'svg']
    
    def ascii_to_image(self, ascii_content, output_path, options=None):
        """
        将ASCII内容转换为图像
        
        Args:
            ascii_content: ASCII图像内容
            output_path: 输出图像路径
            options: 转换选项
            
        Returns:
            dict: 转换结果
        """
        try:
            # 设置默认选项
            default_options = {
                'font_size': 10,
                'font_path': None,
                'bg_color': '#ffffff',
                'fg_color': '#000000',
                'line_spacing': 1.0
            }
            
            if options:
                default_options.update(options)
            
            options = default_options
            
            # 清理ASCII内容
            ascii_content = ascii_content.strip()
            if not ascii_content:
                return {
                    'success': False,
                    'message': 'ASCII内容为空'
                }
            
            # 获取ASCII尺寸
            lines = ascii_content.split('\n')
            max_width = max(len(line) for line in lines)
            height = len(lines)
            
            # 计算图像尺寸
            font_size = options['font_size']
            
            # 尝试获取合适的字体
            try:
                if options['font_path'] and os.path.exists(options['font_path']):
                    font = ImageFont.truetype(options['font_path'], font_size)
                else:
                    # 使用默认字体
                    font = ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()
            
            # 计算字符宽度和高度
            char_width, char_height = font.getbbox('A')[2] - font.getbbox('A')[0], font.getbbox('A')[3] - font.getbbox('A')[1]
            
            # 计算图像宽度和高度
            img_width = max_width * char_width
            img_height = int(height * char_height * options['line_spacing'])
            
            # 创建图像
            img = Image.new('RGB', (img_width, img_height), color=options['bg_color'])
            draw = ImageDraw.Draw(img)
            
            # 绘制ASCII内容
            y = 0
            for line in lines:
                x = 0
                for char in line:
                    draw.text((x, y), char, fill=options['fg_color'], font=font)
                    x += char_width
                y += int(char_height * options['line_spacing'])
            
            # 保存图像
            img.save(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'message': 'ASCII图像转换成功'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'ASCII图像转换失败：{str(e)}'
            }
    
    def batch_convert_ascii(self, input_files, output_dir, options=None):
        """
        批量转换ASCII文件
        
        Args:
            input_files: 输入文件列表
            output_dir: 输出目录
            options: 转换选项
            
        Returns:
            dict: 批量转换结果
        """
        try:
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
                
                # 读取ASCII内容
                with open(input_file, 'r', encoding='utf-8') as f:
                    ascii_content = f.read()
                
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_path = os.path.join(output_dir, f'{base_name}.png')
                
                # 转换
                result = self.ascii_to_image(ascii_content, output_path, options)
                result['file'] = input_file
                results.append(result)
            
            return {
                'success': True,
                'results': results,
                'message': f'批量转换完成，共处理 {len(input_files)} 个文件'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'批量转换失败：{str(e)}'
            }
    
    def detect_ascii_images(self, text_content):
        """
        检测文本中的ASCII图像
        
        Args:
            text_content: 包含可能包含ASCII图像的文本
            
        Returns:
            list: 检测到的ASCII图像列表
        """
        ascii_images = []
        
        # 简单的ASCII图像检测：查找包含大量特殊字符的连续行
        lines = text_content.split('\n')
        ascii_pattern = re.compile(r'[\x20-\x7E]+')  # 可打印ASCII字符
        
        current_ascii = []
        in_ascii_block = False
        
        for i, line in enumerate(lines):
            # 计算行中的特殊字符比例
            printable_chars = ascii_pattern.match(line)
            if printable_chars:
                printable_content = printable_chars.group(0)
                # 跳过空行
                if not printable_content.strip():
                    if in_ascii_block and current_ascii:
                        # 保存当前ASCII块
                        ascii_images.append({
                            'content': '\n'.join(current_ascii),
                            'start_line': i - len(current_ascii),
                            'end_line': i - 1
                        })
                        current_ascii = []
                        in_ascii_block = False
                    continue
                
                # 检查是否包含足够的ASCII字符
                if len(printable_content) > 20 and any(c in '|+-.=*#@$%&' for c in printable_content):
                    current_ascii.append(line)
                    in_ascii_block = True
                else:
                    if in_ascii_block and current_ascii:
                        # 保存当前ASCII块
                        ascii_images.append({
                            'content': '\n'.join(current_ascii),
                            'start_line': i - len(current_ascii),
                            'end_line': i - 1
                        })
                        current_ascii = []
                        in_ascii_block = False
            else:
                if in_ascii_block and current_ascii:
                    # 保存当前ASCII块
                    ascii_images.append({
                        'content': '\n'.join(current_ascii),
                        'start_line': i - len(current_ascii),
                        'end_line': i - 1
                    })
                    current_ascii = []
                    in_ascii_block = False
        
        # 保存最后一个ASCII块
        if in_ascii_block and current_ascii:
            ascii_images.append({
                'content': '\n'.join(current_ascii),
                'start_line': len(lines) - len(current_ascii),
                'end_line': len(lines) - 1
            })
        
        return ascii_images
    
    def convert_text_with_ascii(self, text_content, output_dir, options=None):
        """
        转换文本中的ASCII图像为真实图像，并返回替换后的文本
        
        Args:
            text_content: 包含ASCII图像的文本
            output_dir: 输出图像目录
            options: 转换选项
            
        Returns:
            dict: 转换结果，包含替换后的文本和图像信息
        """
        try:
            # 检测ASCII图像
            ascii_images = self.detect_ascii_images(text_content)
            if not ascii_images:
                return {
                    'success': True,
                    'text': text_content,
                    'images': [],
                    'message': '未检测到ASCII图像'
                }
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 替换ASCII图像
            lines = text_content.split('\n')
            replaced_text = []
            images_info = []
            last_end_line = -1
            
            for i, ascii_img in enumerate(ascii_images):
                # 添加ASCII图像之前的内容
                if ascii_img['start_line'] > last_end_line + 1:
                    replaced_text.extend(lines[last_end_line + 1:ascii_img['start_line']])
                
                # 转换ASCII图像
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                image_name = f'ascii_image_{timestamp}_{i}.png'
                image_path = os.path.join(output_dir, image_name)
                
                result = self.ascii_to_image(ascii_img['content'], image_path, options)
                if result['success']:
                    # 添加图像引用
                    replaced_text.append(f'![ASCII图像 {i+1}]({image_path})')
                    images_info.append({
                        'original_ascii': ascii_img['content'],
                        'image_path': image_path,
                        'start_line': ascii_img['start_line'],
                        'end_line': ascii_img['end_line']
                    })
                else:
                    # 转换失败，保留原始ASCII
                    replaced_text.extend(lines[ascii_img['start_line']:ascii_img['end_line'] + 1])
                
                last_end_line = ascii_img['end_line']
            
            # 添加剩余内容
            if last_end_line < len(lines) - 1:
                replaced_text.extend(lines[last_end_line + 1:])
            
            return {
                'success': True,
                'text': '\n'.join(replaced_text),
                'images': images_info,
                'message': f'成功转换 {len(images_info)} 个ASCII图像'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'转换失败：{str(e)}'
            }
    
    def get_supported_formats(self):
        """
        获取支持的图像格式
        """
        return self.supported_formats