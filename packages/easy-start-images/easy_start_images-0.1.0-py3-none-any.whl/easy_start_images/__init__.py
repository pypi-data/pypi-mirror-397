#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os

from PIL import Image, ImageDraw


def pillow_draw_texts(image_file_path: str = "", image_file_save_kwargs: dict = None, texts: list[dict] = []):
    """
    在图片上绘制多个文本，并保存结果图片。
    
    Args:
        image_file_path (str, optional): 原始图片文件路径。默认值为空字符串。
        image_file_save_kwargs (dict, optional): 图片保存参数，将传递给Image.save()方法。
            至少应包含'fp'键指定保存路径。默认值为None，会被转换为空字典。
        texts (list[dict], optional): 要绘制的文本列表，每个元素是一个字典，包含
            ImageDraw.text()方法所需的参数，如位置'xy'、文本内容'text'、字体'font'、
            颜色'fill'等。默认值为空列表。
            
    Returns:
        tuple: 返回一个元组，包含两个元素：
            - bool: 操作是否成功完成，始终返回True
            - str: 保存的图片文件路径，如果未指定则为空字符串
    """
    # 确保保存参数为字典类型
    image_file_save_kwargs = image_file_save_kwargs if isinstance(image_file_save_kwargs, dict) else dict()
    # 打开原始图片
    image_file = Image.open(image_file_path)
    # 创建绘图对象
    image_draw = ImageDraw.Draw(image_file)
    # 遍历文本列表，绘制每个文本
    for i in texts:
        # 确保文本参数为字典类型
        i = i if isinstance(i, dict) else dict()
        # 绘制文本，使用**i传递所有文本参数
        image_draw.text(**i)
    # 获取保存路径
    fp = image_file_save_kwargs.get("fp", "")
    # 如果保存路径是字符串，确保目录存在
    if isinstance(fp, str):
        os.makedirs(os.path.dirname(fp), exist_ok=True)
    # 保存修改后的图片
    image_file.save(**image_file_save_kwargs)
    # 返回操作结果和保存路径
    return True, image_file_save_kwargs.get("fp", "")