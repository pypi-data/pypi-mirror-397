#!/usr/bin/env python3
"""
图片压缩工具
============

基于 Pillow 的高质量图片压缩工具，专门针对 AI 识别优化。
支持多种格式，智能压缩策略，确保压缩后图片保持清晰度。
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    from PIL import Image, ImageOps
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None
    ImageOps = None

from ..debug import web_debug_log as debug_log


class ImageCompressor:
    """图片压缩器"""
    
    # 压缩配置常量
    TARGET_SIZE = 500 * 1024  # 目标大小 500KB
    COMPRESSION_THRESHOLD = 500 * 1024  # 压缩阈值 500KB
    MAX_DIMENSION = 2048  # 最大尺寸
    MIN_DIMENSION = 400  # 最小尺寸（确保 AI 识别）
    
    # 质量参数
    JPEG_QUALITY_HIGH = 85
    JPEG_QUALITY_MEDIUM = 75
    JPEG_QUALITY_LOW = 65
    JPEG_QUALITY_MIN = 50
    
    # WebP 质量参数（通常比 JPEG 更高效）
    WEBP_QUALITY_HIGH = 80
    WEBP_QUALITY_MEDIUM = 70
    WEBP_QUALITY_LOW = 60
    WEBP_QUALITY_MIN = 45
    
    def __init__(self):
        """初始化压缩器"""
        if not PILLOW_AVAILABLE:
            raise ImportError("Pillow 库未安装，无法使用图片压缩功能")
        
        self.logger = logging.getLogger(__name__)
    
    def compress_image_bytes(
        self, 
        image_data: bytes, 
        target_size: Optional[int] = None,
        format_hint: Optional[str] = None
    ) -> Tuple[bytes, dict]:
        """
        压缩图片字节数据
        
        Args:
            image_data: 原始图片字节数据
            target_size: 目标大小（字节），默认使用 TARGET_SIZE
            format_hint: 格式提示（如 'image/jpeg'）
            
        Returns:
            Tuple[bytes, dict]: (压缩后的字节数据, 压缩信息)
        """
        if not image_data:
            raise ValueError("图片数据为空")
        
        target_size = target_size or self.TARGET_SIZE
        original_size = len(image_data)
        
        debug_log(f"开始压缩图片，原始大小: {self._format_size(original_size)}")
        
        # 如果图片已经小于目标大小，直接返回
        if original_size <= target_size:
            debug_log(f"图片大小 {self._format_size(original_size)} 已小于目标 {self._format_size(target_size)}，无需压缩")
            return image_data, {
                'original_size': original_size,
                'compressed_size': original_size,
                'compression_ratio': 0.0,
                'compressed': False,
                'format': self._detect_format(image_data),
                'dimensions': self._get_image_dimensions(image_data)
            }
        
        try:
            # 打开图片
            with Image.open(io.BytesIO(image_data)) as img:
                # 获取原始信息
                original_format = img.format or 'JPEG'
                original_dimensions = img.size
                
                debug_log(f"原始图片信息: {original_dimensions[0]}x{original_dimensions[1]}, 格式: {original_format}")
                
                # 转换为 RGB（如果需要）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 对于透明图片，使用白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 应用 EXIF 旋转
                img = ImageOps.exif_transpose(img)
                
                # 多轮压缩尝试
                compressed_data, compression_info = self._compress_with_multiple_attempts(
                    img, target_size, original_format, original_dimensions
                )
                
                # 如果仍未达到目标大小，执行自适应降采样循环，直至 <= 目标或到达下限
                min_quality = self.JPEG_QUALITY_MIN
                min_dimension = self.MIN_DIMENSION
                current_img = img
                current_format = compression_info.get('format', 'JPEG')
                current_quality = compression_info.get('quality', self.JPEG_QUALITY_MEDIUM)
                current_data = compressed_data
                
                def encode(image, fmt, quality):
                    out = io.BytesIO()
                    save_kwargs = {'format': fmt}
                    if fmt in ('JPEG','WEBP'):
                        save_kwargs['quality'] = int(max(min(quality, 95), 40))
                        save_kwargs['optimize'] = True
                        if fmt == 'JPEG':
                            save_kwargs['progressive'] = True
                    image.save(out, **save_kwargs)
                    return out.getvalue()
                
                # 自适应循环
                attempt = 0
                while len(current_data) > target_size and \
                      (max(current_img.size) > min_dimension or current_quality > min_quality):
                    attempt += 1
                    # 先降低质量，再必要时按比例缩小
                    if current_quality > min_quality:
                        current_quality = max(min_quality, int(current_quality - 5))
                    else:
                        # 缩放到 90% 尺寸，保持不低于最小尺寸
                        w, h = current_img.size
                        scale = 0.9
                        new_w = max(int(w * scale), min_dimension)
                        new_h = max(int(h * scale), min_dimension)
                        if (new_w, new_h) == current_img.size:
                            # 无法继续缩放，跳出
                            break
                        current_img = current_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    try:
                        current_data = encode(current_img, 'JPEG', current_quality)
                    except Exception:
                        # 回退为 WEBP 尝试
                        try:
                            current_data = encode(current_img, 'WEBP', current_quality)
                            current_format = 'WEBP'
                        except Exception:
                            break
                
                # 计算最终信息
                final_size = len(current_data)
                compression_info.update({
                    'original_size': original_size,
                    'compressed_size': final_size,
                    'compression_ratio': (1 - final_size / original_size) * 100.0,
                    'compressed': True,
                    'original_format': original_format,
                    'original_dimensions': original_dimensions,
                    'format': current_format,
                    'quality': current_quality,
                    'dimensions': current_img.size,
                })
                
                debug_log(
                    f"压缩完成: {self._format_size(original_size)} → {self._format_size(final_size)} "
                    f"(压缩率: {compression_info['compression_ratio']:.1f}%)"
                )
                
                return current_data, compression_info
                
        except Exception as e:
            debug_log(f"图片压缩失败: {e}")
            # 压缩失败时返回原始数据
            return image_data, {
                'original_size': original_size,
                'compressed_size': original_size,
                'compression_ratio': 0.0,
                'compressed': False,
                'error': str(e),
                'format': self._detect_format(image_data),
                'dimensions': self._get_image_dimensions(image_data)
            }
    
    def _compress_with_multiple_attempts(
        self, 
        img: Image.Image, 
        target_size: int, 
        original_format: str,
        original_dimensions: Tuple[int, int]
    ) -> Tuple[bytes, dict]:
        """多轮压缩尝试"""
        
        best_result = None
        best_size = float('inf')
        
        # 尝试不同的压缩策略
        strategies = [
            # 策略1: 保持原始尺寸，降低质量
            {'resize': False, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_HIGH},
            {'resize': False, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_MEDIUM},
            {'resize': False, 'format': 'WEBP', 'quality': self.WEBP_QUALITY_HIGH},
            
            # 策略2: 适度缩放，中等质量
            {'resize': True, 'scale': 0.8, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_MEDIUM},
            {'resize': True, 'scale': 0.8, 'format': 'WEBP', 'quality': self.WEBP_QUALITY_MEDIUM},
            
            # 策略3: 更大缩放，保持质量
            {'resize': True, 'scale': 0.6, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_HIGH},
            {'resize': True, 'scale': 0.6, 'format': 'WEBP', 'quality': self.WEBP_QUALITY_HIGH},
            
            # 策略4: 激进压缩
            {'resize': True, 'scale': 0.5, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_LOW},
            {'resize': True, 'scale': 0.5, 'format': 'WEBP', 'quality': self.WEBP_QUALITY_LOW},
            
            # 策略5: 最后手段
            {'resize': True, 'scale': 0.4, 'format': 'JPEG', 'quality': self.JPEG_QUALITY_MIN},
            {'resize': True, 'scale': 0.4, 'format': 'WEBP', 'quality': self.WEBP_QUALITY_MIN},
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                result_data, info = self._apply_compression_strategy(img, strategy)
                result_size = len(result_data)
                
                # 构造可选的缩放信息，避免在 f-string 表达式中使用反斜杠
                scale_info = f", 缩放: {strategy.get('scale', 1.0):.1f}" if strategy.get('resize') else ""
                debug_log(
                    f"策略 {i}: {self._format_size(result_size)} "
                    f"({strategy['format']}, 质量: {strategy['quality']}{scale_info})"
                )
                
                # 如果达到目标大小，直接返回
                if result_size <= target_size:
                    info['strategy'] = i
                    info['compressed_size'] = result_size
                    return result_data, info
                
                # 记录最佳结果
                if result_size < best_size:
                    best_size = result_size
                    best_result = (result_data, info)
                    best_result[1]['strategy'] = i
                    best_result[1]['compressed_size'] = result_size
                
            except Exception as e:
                debug_log(f"策略 {i} 失败: {e}")
                continue
        
        # 如果没有策略达到目标，返回最佳结果
        if best_result:
            debug_log(f"使用最佳策略 {best_result[1]['strategy']}: {self._format_size(best_size)}")
            return best_result
        
        # 如果所有策略都失败，返回原始图片的 JPEG 版本
        debug_log("所有压缩策略失败，返回基础 JPEG 压缩")
        return self._apply_compression_strategy(img, {
            'resize': False, 
            'format': 'JPEG', 
            'quality': self.JPEG_QUALITY_MEDIUM
        })
    
    def _apply_compression_strategy(self, img: Image.Image, strategy: dict) -> Tuple[bytes, dict]:
        """应用压缩策略"""
        working_img = img.copy()
        
        # 应用缩放
        if strategy.get('resize') and strategy.get('scale'):
            scale = strategy['scale']
            new_width = max(int(working_img.width * scale), self.MIN_DIMENSION)
            new_height = max(int(working_img.height * scale), self.MIN_DIMENSION)
            
            # 确保不超过最大尺寸
            if max(new_width, new_height) > self.MAX_DIMENSION:
                ratio = self.MAX_DIMENSION / max(new_width, new_height)
                new_width = int(new_width * ratio)
                new_height = int(new_height * ratio)
            
            working_img = working_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 保存到字节流
        output = io.BytesIO()
        save_format = strategy['format']
        save_kwargs = {'format': save_format}
        
        if save_format in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = strategy['quality']
            save_kwargs['optimize'] = True
            
        if save_format == 'JPEG':
            save_kwargs['progressive'] = True
        
        working_img.save(output, **save_kwargs)
        compressed_data = output.getvalue()
        
        return compressed_data, {
            'compressed_size': len(compressed_data),
            'format': save_format,
            'quality': strategy['quality'],
            'dimensions': working_img.size,
            'resized': strategy.get('resize', False),
            'scale': strategy.get('scale', 1.0)
        }
    
    def _detect_format(self, image_data: bytes) -> str:
        """检测图片格式"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return img.format or 'UNKNOWN'
        except:
            return 'UNKNOWN'
    
    def _get_image_dimensions(self, image_data: bytes) -> Optional[Tuple[int, int]]:
        """获取图片尺寸"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return img.size
        except:
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


# 全局压缩器实例
_compressor = None

def get_image_compressor() -> ImageCompressor:
    """获取图片压缩器实例（单例模式）"""
    global _compressor
    if _compressor is None:
        _compressor = ImageCompressor()
    return _compressor

def compress_image_if_needed(
    image_data: bytes, 
    target_size: Optional[int] = None,
    format_hint: Optional[str] = None
) -> Tuple[bytes, dict]:
    """
    如果需要则压缩图片的便捷函数
    
    Args:
        image_data: 图片字节数据
        target_size: 目标大小，默认 500KB
        format_hint: 格式提示
        
    Returns:
        Tuple[bytes, dict]: (压缩后数据, 压缩信息)
    """
    if not PILLOW_AVAILABLE:
        debug_log("Pillow 不可用，跳过图片压缩")
        return image_data, {
            'original_size': len(image_data),
            'compressed_size': len(image_data),
            'compression_ratio': 0.0,
            'compressed': False,
            'error': 'Pillow not available'
        }
    
    compressor = get_image_compressor()
    return compressor.compress_image_bytes(image_data, target_size, format_hint)
