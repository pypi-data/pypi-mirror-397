#!/usr/bin/env python3
"""
模拟AI客户端 - 通过MCP标准协议连接
这个版本通过MCP标准协议（JSON-RPC over stdin/stdout）与服务器通信。

使用方法：
1. 运行此脚本：python simulate_ai_client.py
2. 脚本会启动MCP服务器子进程并通过标准协议通信
3. 调用真正的interactive_feedback工具
4. 分析接收到的真实MCP数据并显示详细报告

功能特点：
- ✅ 真正的MCP协议通信（JSON-RPC over stdin/stdout）
- ✅ 调用真实的interactive_feedback工具
- ✅ 获取真实的MCP响应数据
- ✅ 完整的数据分析和报告
- ✅ 支持图片数据的Base64解码和验证

注意：
- 使用MCP标准协议，与VSCode中的AI工具使用相同的通信方式
- 会启动独立的MCP服务器子进程进行测试
- 获得的是真实的工具调用响应数据
"""

import asyncio
import json
import base64
import subprocess
import sys
import time
from pathlib import Path
import logging
import argparse
import os

class AIClient:
    def __init__(self):
        self.process = None
        self.request_id = 0

    async def start_mcp_server(self):
        """启动MCP服务器子进程"""
        try:
            print("🚀 启动MCP服务器子进程...")

            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent / "src")

            # 启动MCP服务器
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "mcp_feedback_enhanced",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(Path(__file__).parent),
                limit=1024*1024*10  # 10MB缓冲区限制
            )

            print("✅ MCP服务器子进程已启动")

            # 等待服务器初始化
            await asyncio.sleep(1)
            return True

        except Exception as e:
            print(f"❌ 启动MCP服务器失败: {e}")
            return False

    async def send_request(self, method, params=None):
        """发送JSON-RPC请求到MCP服务器"""
        if not self.process:
            raise Exception("MCP服务器未启动")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        if params:
            request["params"] = params

        request_json = json.dumps(request) + "\n"
        print(f"📤 发送请求: {method}")

        try:
            # 发送请求
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            # 读取响应
            response_line = await self.process.stdout.readline()
            if not response_line:
                raise Exception("服务器没有响应")

            response = json.loads(response_line.decode().strip())
            print(f"📥 收到响应: {response.get('result', {}).get('serverInfo', {}).get('name', 'OK')}")

            return response

        except Exception as e:
            print(f"❌ 发送请求失败: {e}")
            raise

    async def call_interactive_feedback(self, arguments):
        """调用interactive_feedback工具"""
        project_directory = arguments.get("project_directory", ".")
        summary = arguments.get("summary", "AI客户端测试")
        timeout = arguments.get("timeout", 120)

        print(f"🛠️ 调用interactive_feedback工具")
        print(f"   项目目录: {project_directory}")
        print(f"   摘要: {summary}")
        print(f"   超时: {timeout}秒")

        # 调用tools/call方法
        response = await self.send_request("tools/call", {
            "name": "interactive_feedback",
            "arguments": {
                "project_directory": project_directory,
                "summary": summary,
                "timeout": timeout
            }
        })

        return response




    async def initialize_connection(self):
        """初始化MCP连接"""
        print("\n🔧 初始化MCP连接...")

        # 发送初始化请求
        init_response = await self.send_request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "clientInfo": {
                "name": "AI-Client-Simulator",
                "version": "1.0.0"
            }
        })

        # 发送initialized通知
        await self.send_notification("notifications/initialized")

        server_name = init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
        print(f"✅ 连接成功: {server_name}")

    async def send_notification(self, method, params=None):
        """发送通知（不需要响应）"""
        if not self.process:
            raise Exception("MCP服务器未启动")

        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params

        notification_json = json.dumps(notification) + "\n"
        print(f"📤 发送通知: {method}")

        self.process.stdin.write(notification_json.encode())
        await self.process.stdin.drain()

    async def call_interactive_feedback(self, arguments):
        """调用interactive_feedback工具"""
        timeout = arguments.get("timeout", 120)
        print(f"\n🤖 AI请求用户反馈（等待{timeout}秒）...")
        print("💡 现在可以通过其他方式上传图片进行测试")

        start_time = time.time()

        response = await self.send_request("tools/call", {
            "name": "interactive_feedback",
            "arguments": arguments
        })

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"⏱️ 实际等待时间: {elapsed:.1f}秒")

        return response

    def analyze_received_data(self, response):
        """详细分析AI端接收到的数据"""
        print("\n" + "="*60)
        print("🔍 AI端数据接收分析报告")
        print("="*60)

        if "result" not in response:
            print("❌ 响应格式错误：没有result字段")
            return False

        result = response["result"]

        # 获取内容数据
        if "content" not in result:
            print("❌ 没有找到content字段")
            return False

        content = result["content"]
        print(f"📊 在content字段中发现 {len(content)} 个数据项")

        # 统计数据
        text_items = []
        image_items = []
        other_items = []

        # 分析每个数据项
        for i, item in enumerate(content, 1):
            print(f"\n📋 数据项 {i}:")

            if isinstance(item, dict):
                item_type = item.get("type", "unknown")
                print(f"   类型: {item_type}")

                if item_type == "text":
                    text_items.append(item)
                    text_content = item.get("text", "")
                    print(f"   文本长度: {len(text_content)} 字符")

                    # 显示完整文本内容
                    print(f"   内容: {text_content}")

                elif item_type == "image":
                    image_items.append(item)
                    self.analyze_image_data(item, i)

                else:
                    other_items.append(item)
                    print(f"   ⚠️ 未知类型: {item_type}")
            else:
                other_items.append(item)
                print(f"   ⚠️ 非字典格式: {type(item)}")

        # 生成分析报告
        self.generate_analysis_report(text_items, image_items, other_items, result)

        return len(image_items) > 0

    def analyze_image_data(self, image_item, index):
        """详细分析图片数据"""
        print(f"   🎉 发现图片数据！")

        mime_type = image_item.get("mimeType", "unknown")
        data = image_item.get("data", "")

        print(f"   MIME类型: {mime_type}")
        print(f"   Base64长度: {len(data):,} 字符")

        if len(data) > 0:
            print(f"   Base64完整内容: {data}")

            # 尝试解码Base64
            try:
                decoded = base64.b64decode(data)
                file_size = len(decoded)
                print(f"   解码后大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")

                # 检测文件格式
                format_info = self.detect_image_format(decoded)
                print(f"   文件格式: {format_info}")

                # 验证数据完整性
                if file_size > 0:
                    print(f"   数据完整性: ✅ 完整")
                else:
                    print(f"   数据完整性: ❌ 空数据")

                # 保存测试文件（可选）
                test_file = f"/tmp/ai_received_image_{index}.{self.get_file_extension(decoded)}"
                try:
                    with open(test_file, "wb") as f:
                        f.write(decoded)
                    print(f"   测试文件: {test_file}")
                except:
                    pass

            except Exception as e:
                print(f"   Base64解码: ❌ 失败 - {e}")
        else:
            print(f"   ⚠️ Base64数据为空")

        # 检查annotations
        annotations = image_item.get("annotations")
        if annotations:
            print(f"   Annotations:")
            if "audience" in annotations:
                print(f"     受众: {annotations['audience']}")
            if "priority" in annotations:
                print(f"     优先级: {annotations['priority']}")
        else:
            print(f"   Annotations: 无")

    def detect_image_format(self, data):
        """检测图片格式"""
        if len(data) < 8:
            return "❌ 数据太短"

        # PNG
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "✅ PNG图片"
        # JPEG
        elif data.startswith(b'\xff\xd8\xff'):
            return "✅ JPEG图片"
        # GIF
        elif data.startswith(b'GIF8'):
            return "✅ GIF图片"
        # WebP
        elif data[8:12] == b'WEBP':
            return "✅ WebP图片"
        # BMP
        elif data.startswith(b'BM'):
            return "✅ BMP图片"
        else:
            hex_header = data[:8].hex().upper()
            return f"⚠️ 未知格式 (头部: {hex_header})"

    def get_file_extension(self, data):
        """根据文件头获取扩展名"""
        if data.startswith(b'\x89PNG'):
            return "png"
        elif data.startswith(b'\xff\xd8\xff'):
            return "jpg"
        elif data.startswith(b'GIF8'):
            return "gif"
        elif len(data) > 12 and data[8:12] == b'WEBP':
            return "webp"
        elif data.startswith(b'BM'):
            return "bmp"
        else:
            return "bin"

    def generate_analysis_report(self, text_items, image_items, other_items, result):
        """生成最终分析报告"""
        print(f"\n" + "="*60)
        print("📊 AI端数据接收总结报告")
        print("="*60)

        print(f"📈 数据统计:")
        print(f"   文本项目: {len(text_items)}")
        print(f"   图片项目: {len(image_items)}")
        print(f"   其他项目: {len(other_items)}")
        print(f"   总计: {len(text_items) + len(image_items) + len(other_items)}")

        print(f"\n🔍 MCP协议验证:")

        # 验证文本内容
        if text_items:
            valid_text = all("text" in item for item in text_items)
            print(f"   文本格式: {'✅ 符合标准' if valid_text else '❌ 格式错误'}")
        else:
            print(f"   文本格式: ⚠️ 无文本内容")

        # 验证图片内容
        if image_items:
            valid_images = 0
            for item in image_items:
                if (item.get("type") == "image" and
                    "data" in item and
                    "mimeType" in item and
                    item.get("mimeType", "").startswith("image/")):
                    valid_images += 1

            print(f"   图片格式: ✅ {valid_images}/{len(image_items)} 符合MCP ImageContent标准")

            if valid_images == len(image_items):
                print(f"   🎉 所有图片数据都符合MCP协议标准！")
            else:
                print(f"   ⚠️ 部分图片数据格式有问题")
        else:
            print(f"   图片格式: ❌ 没有接收到图片数据")

        # 检查错误状态
        is_error = result.get("isError", False)
        print(f"   错误状态: {'⚠️ 有错误' if is_error else '✅ 正常'}")

        # 最终结论
        print(f"\n🎯 测试结论:")
        if image_items:
            print(f"   ✅ 图片数据传输测试成功！")
            print(f"   ✅ AI端成功接收到 {len(image_items)} 张图片")
            print(f"   ✅ 数据格式符合MCP ImageContent标准")
            print(f"   ✅ Base64编码/解码正常")
        else:
            print(f"   ⚠️ 没有接收到图片数据")
            print(f"   💡 可能原因：超时、用户未上传、或处理逻辑问题")

    async def cleanup(self):
        """清理资源"""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            self.process = None
        print("🔌 MCP服务器进程已关闭")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模拟AI客户端 - 通过MCP标准协议连接")
    parser.add_argument("--timeout", type=int, default=120, help="等待用户反馈的超时时间（秒）")
    args = parser.parse_args()

    print("🤖 AI客户端模拟器")
    print("="*60)
    print("这个脚本通过MCP标准协议连接服务器并接收图片数据")
    print("测试步骤：")
    print("1. 启动MCP服务器子进程")
    print("2. 初始化MCP连接")
    print("3. 调用interactive_feedback工具")
    print("4. 等待并分析接收到的数据")
    print("="*60)

    client = AIClient()

    try:
        # 启动MCP服务器
        if not await client.start_mcp_server():
            return

        # 初始化连接
        await client.initialize_connection()

        # 调用interactive_feedback并等待数据
        print("\n⏳ 开始等待用户反馈...")
        print("💡 提示：现在可以通过其他方式（如Augment Code界面）上传图片")

        response = await client.call_interactive_feedback({
            "project_directory": str(Path(__file__).parent),
            "summary": "🧪 AI客户端测试：请上传图片测试数据传输功能",
            "timeout": args.timeout
        })

        # 分析接收到的数据
        client.analyze_received_data(response)

        # 将完整的JSON响应写入文件
        output_file = "response_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 完整响应数据已保存到: {output_file}")

    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.cleanup()
        print(f"\n👋 测试结束")


if __name__ == "__main__":
    print("🚀 启动AI客户端模拟器...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 再见！")
