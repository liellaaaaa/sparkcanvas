#!/usr/bin/env python3
"""
TabBar 图标生成脚本
使用 Pillow 库生成简单的图标占位符
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 图标配置
ICON_SIZE = 81
ICON_CONFIGS = {
    'workspace': {
        'name': '工作台',
        'color': '#7A7E83',
        'active_color': '#3c9cff',
        'symbol': '📊'
    },
    'history': {
        'name': '历史',
        'color': '#7A7E83',
        'active_color': '#3c9cff',
        'symbol': '🕐'
    },
    'prompt': {
        'name': 'Prompt',
        'color': '#7A7E83',
        'active_color': '#3c9cff',
        'symbol': '📝'
    },
    'rag': {
        'name': '知识库',
        'color': '#7A7E83',
        'active_color': '#3c9cff',
        'symbol': '📚'
    }
}


def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_icon(name, color, symbol, size=ICON_SIZE):
    """创建图标"""
    # 创建透明背景
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    margin = 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=hex_to_rgb(color) + (255,)
    )
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        # 尝试使用较大的字体
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # 绘制符号（使用 emoji 或文字）
    # 注意：Pillow 对 emoji 支持有限，这里使用简单的文字
    text = symbol if len(symbol) == 1 else name[0]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2 - 5)
    draw.text(position, text, fill=(255, 255, 255, 255), font=font)
    
    return img


def generate_icons():
    """生成所有图标"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for icon_key, config in ICON_CONFIGS.items():
        # 生成未选中状态图标
        icon_normal = create_icon(
            config['name'],
            config['color'],
            config['symbol']
        )
        icon_normal.save(os.path.join(script_dir, f'{icon_key}.png'), 'PNG')
        print(f'[OK] Generated: {icon_key}.png')
        
        # 生成选中状态图标
        icon_active = create_icon(
            config['name'],
            config['active_color'],
            config['symbol']
        )
        icon_active.save(os.path.join(script_dir, f'{icon_key}-active.png'), 'PNG')
        print(f'[OK] Generated: {icon_key}-active.png')
    
    print('\nAll icons generated successfully!')
    print('Note: These are simple placeholder icons. Consider using professional design tools for better icons.')


if __name__ == '__main__':
    try:
        generate_icons()
    except ImportError:
        print('Error: Pillow library is required')
        print('Please run: pip install Pillow')
    except Exception as e:
        print(f'Error generating icons: {e}')

