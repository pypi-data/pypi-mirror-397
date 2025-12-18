#!/usr/bin/env python3
"""
检测MCP客户端协议版本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.types import TextContent, ImageContent


def detect_mcp_version():
    """检测MCP协议版本和客户端支持情况"""
    print("🔍 检测MCP协议版本和客户端支持")
    
    # 1. 检查MCP types模块
    print("\n1️⃣ 检查MCP types模块")
    try:
        import mcp.types as types
        print(f"   mcp.types模块: ✅ 可用")
        
        # 检查可用的类型
        available_types = []
        for attr_name in dir(types):
            if not attr_name.startswith('_'):
                attr = getattr(types, attr_name)
                if isinstance(attr, type):
                    available_types.append(attr_name)
        
        print(f"   可用类型: {', '.join(sorted(available_types))}")
        
        # 检查关键类型
        key_types = ['TextContent', 'ImageContent', 'EmbeddedResource', 'BlobResourceContents']
        for key_type in key_types:
            if hasattr(types, key_type):
                print(f"   {key_type}: ✅ 支持")
            else:
                print(f"   {key_type}: ❌ 不支持")
                
    except ImportError as e:
        print(f"   mcp.types模块: ❌ 导入失败 - {e}")
        return False
    
    # 2. 测试ImageContent创建
    print("\n2️⃣ 测试ImageContent创建")
    try:
        test_image = ImageContent(
            type="image",
            data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1Pe",
            mimeType="image/png"
        )
        print(f"   ImageContent创建: ✅ 成功")
        print(f"   类型: {type(test_image)}")
        print(f"   属性: type={test_image.type}, mimeType={test_image.mimeType}")
        
        # 检查序列化
        if hasattr(test_image, 'model_dump'):
            dump = test_image.model_dump()
            print(f"   序列化方法: model_dump() ✅")
            print(f"   序列化结果: {list(dump.keys())}")
        elif hasattr(test_image, 'dict'):
            dump = test_image.dict()
            print(f"   序列化方法: dict() ✅")
            print(f"   序列化结果: {list(dump.keys())}")
        else:
            print(f"   序列化方法: ❌ 无标准方法")
            
    except Exception as e:
        print(f"   ImageContent创建: ❌ 失败 - {e}")
        return False
    
    # 3. 检查FastMCP版本
    print("\n3️⃣ 检查FastMCP版本")
    try:
        from fastmcp import FastMCP
        print(f"   FastMCP: ✅ 可用")
        
        # 尝试获取版本信息
        if hasattr(FastMCP, '__version__'):
            print(f"   版本: {FastMCP.__version__}")
        else:
            print(f"   版本: 未知")
            
    except ImportError as e:
        print(f"   FastMCP: ❌ 导入失败 - {e}")
    
    # 4. 检查MCP协议特性
    print("\n4️⃣ 检查MCP协议特性")
    
    # 检查是否支持2025-06-18特性
    features_2025_06_18 = {
        "ImageContent": hasattr(types, 'ImageContent'),
        "EmbeddedResource": hasattr(types, 'EmbeddedResource'),
        "BlobResourceContents": hasattr(types, 'BlobResourceContents'),
    }
    
    supported_features = sum(features_2025_06_18.values())
    total_features = len(features_2025_06_18)
    
    print(f"   2025-06-18特性支持: {supported_features}/{total_features}")
    for feature, supported in features_2025_06_18.items():
        status = "✅" if supported else "❌"
        print(f"     {feature}: {status}")
    
    # 5. 协议版本推断
    print("\n5️⃣ 协议版本推断")
    
    if supported_features == total_features:
        version_estimate = "2025-06-18或更新"
        compatibility = "完全兼容"
        image_support = "应该完全支持ImageContent"
    elif supported_features >= total_features * 0.7:
        version_estimate = "接近2025-06-18"
        compatibility = "部分兼容"
        image_support = "可能部分支持ImageContent"
    else:
        version_estimate = "2025-06-18之前"
        compatibility = "有限兼容"
        image_support = "可能不支持ImageContent显示"
    
    print(f"   估计协议版本: {version_estimate}")
    print(f"   兼容性: {compatibility}")
    print(f"   图片支持: {image_support}")
    
    # 6. 建议
    print("\n6️⃣ 建议")
    
    if supported_features == total_features:
        print("   ✅ 您的MCP环境支持最新特性")
        print("   💡 如果图片仍无法显示，问题可能在客户端渲染层")
        print("   🔧 建议：检查MCP客户端的ImageContent处理实现")
    else:
        print("   ⚠️ 您的MCP环境可能不完全支持最新特性")
        print("   💡 建议升级到最新版本的MCP Python SDK")
        print("   🔧 或者使用向后兼容的文本格式传输图片信息")
    
    return True


if __name__ == "__main__":
    success = detect_mcp_version()
    sys.exit(0 if success else 1)
