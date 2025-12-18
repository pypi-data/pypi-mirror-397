#!/usr/bin/env python3
"""
MCP Feedback Enhanced 伺服器主要模組

此模組提供 MCP (Model Context Protocol) 的增強回饋收集功能，
支援智能環境檢測，自動使用 Web UI 介面。

主要功能：
- MCP 工具實現
- 介面選擇（Web UI）
- 環境檢測 (SSH Remote, WSL, Local)
- 國際化支援
- 圖片處理與上傳
- 命令執行與結果展示
- 專案目錄管理

主要 MCP 工具：
- interactive_feedback: 收集用戶互動回饋
- get_system_info: 獲取系統環境資訊

作者: Fábio Ferreira (原作者)
增強: Minidoracat (Web UI, 圖片支援, 環境檢測)
重構: 模塊化設計
"""

import base64
import io
import json
import os
import sys
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image as MCPImage
from mcp.types import TextContent, ImageContent
from pydantic import Field, BaseModel

# 導入統一的調試功能
from .debug import server_debug_log as debug_log

# 模块级变量：在 main() 中设置，在 interactive_feedback 中使用
_startup_ai_client_type: str = ""




# 定義符合標準協議的ImageContent類
class StandardImageContent(BaseModel):
    """符合MCP標準協議的ImageContent格式"""
    type: str = "image"
    image: dict  # 包含 data, mimeType, name, description 字段

    def dict(self, **kwargs):
        """重写dict方法，确保返回正确的格式"""
        return {
            "type": self.type,
            "image": self.image
        }

    class Config:
        # 允许任意字段，确保兼容性
        extra = "allow"

# 導入多語系支援
# 導入錯誤處理框架
from .utils.error_handler import ErrorHandler, ErrorType

# 導入資源管理器
from .utils.resource_manager import create_temp_file


# ===== 編碼初始化 =====
def init_encoding():
    """初始化編碼設置，確保正確處理中文字符"""
    try:
        # Windows 特殊處理
        if sys.platform == "win32":
            import msvcrt

            # 設置為二進制模式
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

            # 重新包裝為 UTF-8 文本流，並禁用緩衝
            # 修復 union-attr 錯誤 - 安全獲取 buffer 或 detach
            stdin_buffer = getattr(sys.stdin, "buffer", None)
            if stdin_buffer is None and hasattr(sys.stdin, "detach"):
                stdin_buffer = sys.stdin.detach()

            stdout_buffer = getattr(sys.stdout, "buffer", None)
            if stdout_buffer is None and hasattr(sys.stdout, "detach"):
                stdout_buffer = sys.stdout.detach()

            sys.stdin = io.TextIOWrapper(
                stdin_buffer, encoding="utf-8", errors="replace", newline=None
            )
            sys.stdout = io.TextIOWrapper(
                stdout_buffer,
                encoding="utf-8",
                errors="replace",
                newline="",
                write_through=True,  # 關鍵：禁用寫入緩衝
            )
        else:
            # 非 Windows 系統的標準設置
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")

        # 設置 stderr 編碼（用於調試訊息）
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

        return True
    except Exception:
        # 如果編碼設置失敗，嘗試基本設置
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except:
            pass
        return False


# 初始化編碼（在導入時就執行）
_encoding_initialized = init_encoding()

# ===== 常數定義 =====
SERVER_NAME = "互動式回饋收集 MCP"
SSH_ENV_VARS = ["SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY"]
REMOTE_ENV_VARS = ["REMOTE_CONTAINERS", "CODESPACES"]


# 初始化 MCP 服務器
from . import __version__


# 確保 log_level 設定為正確的大寫格式
fastmcp_settings = {}

# 檢查環境變數並設定正確的 log_level
env_log_level = os.getenv("FASTMCP_LOG_LEVEL", "").upper()
if env_log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    fastmcp_settings["log_level"] = env_log_level
else:
    # 預設使用 INFO 等級
    fastmcp_settings["log_level"] = "INFO"

mcp: Any = FastMCP(SERVER_NAME)


# ===== 工具函數 =====
def is_wsl_environment() -> bool:
    """
    檢測是否在 WSL (Windows Subsystem for Linux) 環境中運行

    Returns:
        bool: True 表示 WSL 環境，False 表示其他環境
    """
    try:
        # 檢查 /proc/version 文件是否包含 WSL 標識
        if os.path.exists("/proc/version"):
            with open("/proc/version") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    debug_log("偵測到 WSL 環境（通過 /proc/version）")
                    return True

        # 檢查 WSL 相關環境變數
        wsl_env_vars = ["WSL_DISTRO_NAME", "WSL_INTEROP", "WSLENV"]
        for env_var in wsl_env_vars:
            if os.getenv(env_var):
                debug_log(f"偵測到 WSL 環境變數: {env_var}")
                return True

        # 檢查是否存在 WSL 特有的路徑
        wsl_paths = ["/mnt/c", "/mnt/d", "/proc/sys/fs/binfmt_misc/WSLInterop"]
        for path in wsl_paths:
            if os.path.exists(path):
                debug_log(f"偵測到 WSL 特有路徑: {path}")
                return True

    except Exception as e:
        debug_log(f"WSL 檢測過程中發生錯誤: {e}")

    return False


def is_remote_environment() -> bool:
    """
    檢測是否在遠端環境中運行

    Returns:
        bool: True 表示遠端環境，False 表示本地環境
    """
    # WSL 不應被視為遠端環境，因為它可以訪問 Windows 瀏覽器
    if is_wsl_environment():
        debug_log("WSL 環境不被視為遠端環境")
        return False

    # 檢查 SSH 連線指標
    for env_var in SSH_ENV_VARS:
        if os.getenv(env_var):
            debug_log(f"偵測到 SSH 環境變數: {env_var}")
            return True

    # 檢查遠端開發環境
    for env_var in REMOTE_ENV_VARS:
        if os.getenv(env_var):
            debug_log(f"偵測到遠端開發環境: {env_var}")
            return True

    # 檢查 Docker 容器
    if os.path.exists("/.dockerenv"):
        debug_log("偵測到 Docker 容器環境")
        return True

    # Windows 遠端桌面檢查
    if sys.platform == "win32":
        session_name = os.getenv("SESSIONNAME", "")
        if session_name and "RDP" in session_name:
            debug_log(f"偵測到 Windows 遠端桌面: {session_name}")
            return True

    # Linux 無顯示環境檢查（但排除 WSL）
    if (
        sys.platform.startswith("linux")
        and not os.getenv("DISPLAY")
        and not is_wsl_environment()
    ):
        debug_log("偵測到 Linux 無顯示環境")
        return True

    return False


def save_feedback_to_file(feedback_data: dict, file_path: str | None = None) -> str:
    """
    將回饋資料儲存到 JSON 文件

    Args:
        feedback_data: 回饋資料字典
        file_path: 儲存路徑，若為 None 則自動產生臨時文件

    Returns:
        str: 儲存的文件路徑
    """
    if file_path is None:
        # 使用資源管理器創建臨時文件
        file_path = create_temp_file(suffix=".json", prefix="feedback_")

    # 確保目錄存在
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # 複製數據以避免修改原始數據
    json_data = feedback_data.copy()

    # 處理圖片數據：將 bytes 轉換為 base64 字符串以便 JSON 序列化
    if "images" in json_data and isinstance(json_data["images"], list):
        processed_images = []
        for img in json_data["images"]:
            if isinstance(img, dict) and "data" in img:
                processed_img = img.copy()
                # 如果 data 是 bytes，轉換為 base64 字符串
                if isinstance(img["data"], bytes):
                    processed_img["data"] = base64.b64encode(img["data"]).decode(
                        "utf-8"
                    )
                    processed_img["data_type"] = "base64"
                processed_images.append(processed_img)
            else:
                processed_images.append(img)
        json_data["images"] = processed_images

    # 儲存資料
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    debug_log(f"回饋資料已儲存至: {file_path}")
    return file_path


def create_feedback_text(feedback_data: dict, include_image_summary: bool = False) -> str:
    """
    建立格式化的回饋文字

    Args:
        feedback_data: 回饋資料字典
        include_image_summary: 是否包含圖片概要（當使用標準協議格式時應設為False）

    Returns:
        str: 格式化後的回饋文字
    """
    text_parts = []

    # 基本回饋內容
    if feedback_data.get("interactive_feedback"):
        text_parts.append(f"=== 用戶回饋 ===\n{feedback_data['interactive_feedback']}")

    # 命令執行日誌
    if feedback_data.get("command_logs"):
        text_parts.append(f"=== 命令執行日誌 ===\n{feedback_data['command_logs']}")

    # 圖片附件概要（僅在明確要求時包含）
    if feedback_data.get("images") and include_image_summary:
        images = feedback_data["images"]
        text_parts.append(f"=== 圖片附件概要 ===\n用戶提供了 {len(images)} 張圖片：")

        for i, img in enumerate(images, 1):
            size = img.get("size", 0)
            name = img.get("name", "unknown")

            # 智能單位顯示
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_kb = size / 1024
                size_str = f"{size_kb:.1f} KB"
            else:
                size_mb = size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"

            img_info = f"  {i}. {name} ({size_str})"

            # 為提高兼容性，添加 base64 預覽信息
            if img.get("data"):
                try:
                    if isinstance(img["data"], bytes):
                        img_base64 = base64.b64encode(img["data"]).decode("utf-8")
                    elif isinstance(img["data"], str):
                        img_base64 = img["data"]
                    else:
                        img_base64 = None

                    if img_base64:
                        # 只顯示前50個字符的預覽
                        preview = (
                            img_base64[:50] + "..."
                            if len(img_base64) > 50
                            else img_base64
                        )
                        img_info += f"\n     Base64 預覽: {preview}"
                        img_info += f"\n     完整 Base64 長度: {len(img_base64)} 字符"

                        # 如果 AI 助手不支援 MCP 圖片，可以提供完整 base64
                        debug_log(f"圖片 {i} Base64 已準備，長度: {len(img_base64)}")

                        # 檢查是否啟用 Base64 詳細模式（從 UI 設定中獲取）
                        include_full_base64 = feedback_data.get("settings", {}).get(
                            "enable_base64_detail", False
                        )

                        if include_full_base64:
                            # 根據檔案名推斷 MIME 類型
                            file_name = img.get("name", "image.png")
                            if file_name.lower().endswith((".jpg", ".jpeg")):
                                mime_type = "image/jpeg"
                            elif file_name.lower().endswith(".gif"):
                                mime_type = "image/gif"
                            elif file_name.lower().endswith(".webp"):
                                mime_type = "image/webp"
                            else:
                                mime_type = "image/png"

                            img_info += f"\n     完整 Base64: data:{mime_type};base64,{img_base64}"

                except Exception as e:
                    debug_log(f"圖片 {i} Base64 處理失敗: {e}")

            text_parts.append(img_info)

        # 添加兼容性說明
        text_parts.append(
            "\n💡 注意：如果 AI 助手無法顯示圖片，圖片數據已包含在上述 Base64 信息中。"
        )

    return "\n\n".join(text_parts) if text_parts else "用戶未提供任何回饋內容。"


def create_feedback_text_with_base64(feedback_data: dict) -> str:
    """
    為 Augment 客戶端建立簡潔的 JSON 格式

    當 is_augment_client 為 true 時，圖片將保存到臨時文件並返回絕對路徑，
    而不是 base64 數據，以便後續處理。

    Args:
        feedback_data: 回饋資料字典

    Returns:
        str: 簡潔的 JSON 字符串
    """
    debug_log(f"[AUGMENT_FORMAT] 開始創建簡潔 JSON 格式")

    # 構建簡潔的數據結構
    # 處理用戶回饋文本，添加適當的前綴以保持一致性
    feedback_text = feedback_data.get("interactive_feedback", "").strip()
    if feedback_text:
        formatted_text = f"用戶回饋：{feedback_text}"
    else:
        formatted_text = "用戶未提供回饋"

    # 添加命令日誌（如果有的話）
    logs = feedback_data.get("logs", "") or feedback_data.get("command_logs", "")
    if logs and logs.strip():
        formatted_text += f"\n\n執行日誌：{logs.strip()}"

    simple_data = {
        "text": formatted_text,
        "images": []
    }

    # 處理圖片數據
    images = feedback_data.get("images", [])
    if images:
        debug_log(f"[AUGMENT_FORMAT] 處理 {len(images)} 張圖片")

        for i, img in enumerate(images, 1):
            try:
                # 獲取圖片數據
                img_data = None
                if img.get("data"):
                    if isinstance(img["data"], bytes):
                        img_data = img["data"]
                        debug_log(f"圖片 {i} 使用 bytes 數據，大小: {len(img_data)} bytes")
                    elif isinstance(img["data"], str):
                        # 如果是 base64 字符串，解碼為 bytes
                        img_data = base64.b64decode(img["data"])
                        debug_log(f"圖片 {i} 從 base64 解碼，大小: {len(img_data)} bytes")

                if img_data:
                    # 检测实际图片格式（而不是仅基于文件名）
                    actual_format = _detect_image_format(img_data)
                    name = img.get("name", f"image_{i}")

                    # 根据实际格式设置类型和扩展名
                    if actual_format.upper() in ('JPEG', 'JPG'):
                        img_type = "jpeg"
                        file_ext = ".jpg"
                    elif actual_format.upper() == 'GIF':
                        img_type = "gif"
                        file_ext = ".gif"
                    elif actual_format.upper() == 'WEBP':
                        img_type = "webp"
                        file_ext = ".webp"
                    elif actual_format.upper() == 'PNG':
                        img_type = "png"
                        file_ext = ".png"
                    else:
                        # 如果无法检测格式，回退到基于文件名的推断
                        if name.lower().endswith((".jpg", ".jpeg")):
                            img_type = "jpeg"
                            file_ext = ".jpg"
                        elif name.lower().endswith(".gif"):
                            img_type = "gif"
                            file_ext = ".gif"
                        elif name.lower().endswith(".webp"):
                            img_type = "webp"
                            file_ext = ".webp"
                        else:
                            img_type = "png"
                            file_ext = ".png"

                    debug_log(f"圖片 {i} 格式檢測: 實際格式={actual_format}, 設定類型={img_type}, 擴展名={file_ext}")

                    # 創建臨時文件保存圖片（二進制模式）
                    try:
                        temp_file_path = create_temp_file(
                            suffix=file_ext,
                            prefix=f"augment_image_{i}_",
                            text=False  # 二進制模式，適用於圖片文件
                        )

                        # 將圖片數據寫入臨時文件
                        with open(temp_file_path, 'wb') as f:
                            f.write(img_data)

                        debug_log(f"圖片 {i} 已保存到臨時文件: {temp_file_path}")

                        # 創建圖片對象：包含文件路徑和類型
                        img_obj = {
                            "path": temp_file_path,  # 使用絕對路徑替代 base64 數據
                            "type": img_type
                        }

                        simple_data["images"].append(img_obj)
                        debug_log(f"圖片 {i} 已添加，類型: {img_type}，路徑: {temp_file_path}")

                    except Exception as file_error:
                        debug_log(f"圖片 {i} 保存到臨時文件失敗: {file_error}")
                        # 如果保存失敗，跳過這張圖片
                        continue

                else:
                    debug_log(f"圖片 {i} 數據處理失敗，跳過")

            except Exception as e:
                debug_log(f"圖片 {i} 處理失敗: {e}")
                continue

    # 轉換為 JSON 字符串
    try:
        json_result = json.dumps(simple_data, ensure_ascii=False, separators=(',', ':'))
        debug_log(f"[AUGMENT_FORMAT] 簡潔 JSON 創建成功，長度: {len(json_result)} 字符")
        return json_result
    except Exception as e:
        debug_log(f"[AUGMENT_FORMAT] JSON 序列化失敗: {e}")
        # 回退到最簡格式
        return json.dumps({
            "text": simple_data["text"],
            "images": []
        }, ensure_ascii=False)


def process_images(images_data: list[dict]) -> list[dict]:
    """
    處理圖片資料，轉換為標準 MCP ImageContent 對象

    Args:
        images_data: 圖片資料列表

    Returns:
        List[dict]: 標準 MCP ImageContent 格式的字典列表
    """
    image_contents = []

    for i, img in enumerate(images_data, 1):
        try:
            if not img.get("data"):
                debug_log(f"圖片 {i} 沒有資料，跳過")
                continue

            # 檢查數據類型並相應處理
            if isinstance(img["data"], bytes):
                # 如果是原始 bytes 數據，直接使用
                image_bytes = img["data"]
                debug_log(
                    f"圖片 {i} 使用原始 bytes 數據，大小: {len(image_bytes)} bytes"
                )
            elif isinstance(img["data"], str):
                # 如果是 base64 字符串，進行解碼
                image_bytes = base64.b64decode(img["data"])
                debug_log(f"圖片 {i} 從 base64 解碼，大小: {len(image_bytes)} bytes")
            else:
                debug_log(f"圖片 {i} 數據類型不支援: {type(img['data'])}")
                continue

            if len(image_bytes) == 0:
                debug_log(f"圖片 {i} 數據為空，跳過")
                continue

            # 根據文件名推斷 MIME 類型
            file_name = img.get("name", "image.png")
            if file_name.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif file_name.lower().endswith(".gif"):
                mime_type = "image/gif"
            elif file_name.lower().endswith(".webp"):
                mime_type = "image/webp"
            else:
                mime_type = "image/png"  # 默認使用 PNG

            # 將 bytes 轉換為 base64 字符串（MCP ImageContent 標準格式）
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # 計算文件大小
            file_size_kb = len(image_bytes) / 1024
            image_name = img.get("name", f"image_{i}.png")

            # 使用標準MCP ImageContent類
            # 根據Context7文檔，ImageContent應該有data和mimeType字段
            try:
                image_content = ImageContent(
                    type="image",
                    data=image_base64,  # 使用base64字符串
                    mimeType=mime_type
                )
                debug_log(f"圖片 {i} 使用標準ImageContent創建成功")
            except Exception as e:
                debug_log(f"ImageContent創建失敗: {e}")
                # 如果ImageContent不支持這種格式，回退到字典
                image_content = {
                    "type": "image",
                    "data": image_base64,
                    "mimeType": mime_type
                }

            image_contents.append(image_content)

            debug_log(f"圖片 {i} ({image_name}) 處理成功，MIME類型: {mime_type}，base64長度: {len(image_base64)}")

            # 根據image_content的類型記錄不同信息
            if hasattr(image_content, 'mimeType'):
                debug_log(f"圖片 {i} ImageContent對象已創建: mimeType={image_content.mimeType}")
            elif isinstance(image_content, dict):
                debug_log(f"圖片 {i} 字典格式已創建: mimeType={image_content.get('mimeType')}")

        except Exception as e:
            # 使用統一錯誤處理（不影響 JSON RPC）
            error_id = ErrorHandler.log_error_with_context(
                e,
                context={"operation": "圖片處理", "image_index": i},
                error_type=ErrorType.FILE_IO,
            )
            debug_log(f"圖片 {i} 處理失敗 [錯誤ID: {error_id}]: {e}")

    debug_log(f"共處理 {len(image_contents)} 張圖片")
    return image_contents


def _detect_image_format(image_data: bytes) -> str:
    """
    检测图片的实际格式

    Args:
        image_data: 图片字节数据

    Returns:
        str: 图片格式 (PNG, JPEG, GIF, WEBP, UNKNOWN)
    """
    try:
        # 检查文件头魔数
        if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'PNG'
        elif image_data.startswith(b'\xff\xd8\xff'):
            return 'JPEG'
        elif image_data.startswith(b'GIF8'):
            return 'GIF'
        elif len(image_data) > 12 and image_data[8:12] == b'WEBP':
            return 'WEBP'
        elif image_data.startswith(b'BM'):
            return 'BMP'
        else:
            # 尝试使用PIL检测
            try:
                from PIL import Image
                with Image.open(io.BytesIO(image_data)) as img:
                    return img.format or 'UNKNOWN'
            except:
                return 'UNKNOWN'
    except Exception as e:
        debug_log(f"图片格式检测失败: {e}")
        return 'UNKNOWN'


# ===== MCP 工具定義 =====
@mcp.tool()
async def interactive_feedback(
    project_directory: Annotated[str, Field(description="專案目錄路徑")] = ".",
    summary: Annotated[
        str, Field(description="AI 工作完成的摘要說明")
    ] = "我已完成了您請求的任務。",
    timeout: Annotated[int, Field(description="等待用戶回饋的超時時間（秒）")] = 600,
) -> list:
    """Interactive feedback collection tool for LLM agents.

    USAGE RULES:
    1. During any process, task, or conversation, whether asking, replying, or completing phased tasks, you must call this tool to ask for feedback.
    2. Unless receiving termination instructions, all steps must repeatedly call this tool.
    3. Whenever user feedback is received, if the feedback content is not empty, you must call this tool again and adjust behavior based on the feedback content.
    4. Only when the user explicitly indicates "end" or "no more interaction needed" can you stop calling this tool, and the process is considered complete.
    5. You should summarize what have done, and provide project directory through args to let user know what you have done to provide feedback for next step.

    Args:
        project_directory: Project directory path for context
        summary: Summary of AI work completed for user review
        timeout: Timeout in seconds for waiting user feedback (default: 600 seconds)

    Returns:
        list: List containing TextContent and ImageContent objects representing user feedback in standard MCP format
    """
    # 環境偵測
    is_remote = is_remote_environment()
    is_wsl = is_wsl_environment()

    # 使用服务器启动时的固定配置（不再重新读取环境变量）
    current_ai_client_type = _startup_ai_client_type
    is_augment_client = current_ai_client_type == 'augment'

    print(f"[SERVER_CONFIG] 当前进程PID: {os.getpid()}", file=sys.stderr)
    print(f"[SERVER_CONFIG] 使用服务器启动时的固定配置: {current_ai_client_type!r}", file=sys.stderr)
    print(f"[SERVER_CONFIG] is_augment_client = {is_augment_client}", file=sys.stderr)
    print(f"[SERVER_CONFIG] 配置来源: 服务器启动时环境变量", file=sys.stderr)

    debug_log(f"環境偵測結果 - 遠端: {is_remote}, WSL: {is_wsl}")
    debug_log("使用介面: Web UI")

    try:
        # 確保專案目錄存在
        if not os.path.exists(project_directory):
            project_directory = os.getcwd()
        project_directory = os.path.abspath(project_directory)

        # 使用 Web 模式
        debug_log("回饋模式: web")

        # 在啟動 Web UI 之前，確保 WebUIManager 能夠獲取到正確的 AI 客戶端類型
        from .web import get_web_ui_manager
        from .web.main import _web_ui_manager

        # 如果 WebUIManager 還沒有創建，我們需要確保它能獲取到正確的 AI 客戶端類型
        manager = get_web_ui_manager()

        # 檢查 WebUIManager 是否正確讀取了 AI 客戶端類型
        if manager.ai_client_type != current_ai_client_type:
            debug_log(f"WebUIManager AI 客戶端類型不匹配: manager={manager.ai_client_type}, expected={current_ai_client_type}")
            debug_log(f"強制更新 WebUIManager 的 AI 客戶端類型")
            manager.ai_client_type = current_ai_client_type
            # 同時更新保存的環境變數
            manager.env_vars['MCP_AI_CLIENT'] = current_ai_client_type

        # 現在啟動 Web UI
        result = await launch_web_feedback_ui(project_directory, summary, timeout)

        # 處理取消情況
        if not result:
            return [TextContent(type="text", text="用戶取消了回饋。")]

        # 儲存詳細結果
        save_feedback_to_file(result)

        # 建立回饋項目列表
        feedback_items = []

        # 根據 AI 客戶端類型決定返回格式（使用直接读取的值确保可靠性）
        print(f"[FINAL_CHECK] 最终判断：current_ai_client_type = '{current_ai_client_type}'", file=sys.stderr)
        print(f"[FINAL_CHECK] 最终判断：is_augment_client = {is_augment_client}", file=sys.stderr)
        if is_augment_client:
            # Augment 客戶端：根據是否有圖片決定格式
            images = result.get("images", [])
            has_images = bool(images and any(img.get("data") for img in images))

            if has_images:
                # 有圖片：使用 JSON 格式便於 JavaScript 提取
                debug_log("有圖片數據，使用 JSON 格式返回")
                json_text = create_feedback_text_with_base64(result)
                return [TextContent(type="text", text=json_text)]
            else:
                # 無圖片：使用普通文本格式便於閱讀
                debug_log("無圖片數據，使用文本格式返回")
                text_parts = []

                # 用戶回饋
                feedback = result.get("interactive_feedback", "").strip()
                if feedback:
                    text_parts.append(f"用戶回饋：{feedback}")
                else:
                    text_parts.append("用戶未提供回饋")

                # 命令日誌
                logs = result.get("logs", "") or result.get("command_logs", "")
                if logs and logs.strip():
                    text_parts.append(f"執行日誌：{logs.strip()}")

                combined_text = "\n\n".join(text_parts) if text_parts else "無回饋內容"
                return [TextContent(type="text", text=combined_text)]
        else:
            # 標準客戶端：分別返回文字和圖片
            debug_log("使用標準格式：文字和圖片分別傳輸")

            # 添加文字回饋（不包含圖片概要，因為圖片將以標準協議格式單獨傳輸）
            if result.get("interactive_feedback") or result.get("command_logs"):
                feedback_text = create_feedback_text(result, include_image_summary=False)
                feedback_items.append(TextContent(type="text", text=feedback_text))
                debug_log("文字回饋已添加")

            # 添加圖片回饋（採用cunzhi項目的成功策略：圖片優先，文本在後）
            if result.get("images"):
                image_contents = process_images(result["images"])
                # 🎯 關鍵策略：圖片優先添加（模仿cunzhi項目）
                # 直接添加圖片字典對象，不嵌套在JSON字符串中
                feedback_items.extend(image_contents)
                debug_log(f"已添加 {len(image_contents)} 張圖片（直接字典格式）")

                # 不再添加詳細圖片信息到文本中，因為圖片數據已經以標準協議格式單獨傳輸
                debug_log(f"圖片數據將以標準協議格式單獨傳輸，不添加到文本中")

            # 確保至少有一個回饋項目
            if not feedback_items:
                feedback_items.append(
                    TextContent(type="text", text="用戶未提供任何回饋內容。")
                )

            debug_log(f"回饋收集完成，原始項目數: {len(feedback_items)}")

            # 標準模式：處理並轉換所有項目
            # 將StandardImageContent對象轉換為字典
            final_items = []

            for item in feedback_items:
                if isinstance(item, StandardImageContent):
                    # 將StandardImageContent轉換為字典
                    final_items.append({
                        "type": "image",
                        "image": item.image
                    })
                    debug_log(f"StandardImageContent已轉換為字典格式")
                else:
                    # 其他項目直接添加
                    final_items.append(item)

            debug_log(f"最終返回項目數: {len(final_items)}")
            return final_items

    except Exception as e:
        # 使用統一錯誤處理，但不影響 JSON RPC 響應
        error_id = ErrorHandler.log_error_with_context(
            e,
            context={"operation": "回饋收集", "project_dir": project_directory},
            error_type=ErrorType.SYSTEM,
        )

        # 生成用戶友好的錯誤信息
        user_error_msg = ErrorHandler.format_user_error(e, include_technical=True)  # 暂时显示技术细节
        debug_log(f"回饋收集錯誤 [錯誤ID: {error_id}]: {e!s}")
        debug_log(f"錯誤堆棧: {e.__class__.__name__}: {e}")

        # 根據 AI 客戶端類型決定錯誤響應格式
        print(f"[ERROR_FORMAT] 錯誤處理：current_ai_client_type = '{current_ai_client_type}'", file=sys.stderr)
        print(f"[ERROR_FORMAT] 錯誤處理：is_augment_client = {is_augment_client}", file=sys.stderr)

        if is_augment_client:
            # Augment 客戶端：錯誤時使用簡單文本格式（因為沒有圖片）
            debug_log("使用 Augment 文本格式返回錯誤信息")
            error_text = f"❌ 操作超时\n技術細節：{user_error_msg}"
            return [TextContent(type="text", text=error_text)]
        else:
            # 標準客戶端：直接返回錯誤信息
            debug_log("使用標準格式返回錯誤信息")
            return [TextContent(type="text", text=user_error_msg)]


async def launch_web_feedback_ui(project_dir: str, summary: str, timeout: int) -> dict:
    """
    啟動 Web UI 收集回饋，支援自訂超時時間

    Args:
        project_dir: 專案目錄路徑
        summary: AI 工作摘要
        timeout: 超時時間（秒）

    Returns:
        dict: 收集到的回饋資料
    """
    debug_log(f"啟動 Web UI 介面，超時時間: {timeout} 秒")

    try:
        # 使用新的 web 模組
        from .web import launch_web_feedback_ui as web_launch

        # 傳遞 timeout 參數給 Web UI
        return await web_launch(project_dir, summary, timeout)
    except ImportError as e:
        # 使用統一錯誤處理
        error_id = ErrorHandler.log_error_with_context(
            e,
            context={"operation": "Web UI 模組導入", "module": "web"},
            error_type=ErrorType.DEPENDENCY,
        )
        user_error_msg = ErrorHandler.format_user_error(
            e, ErrorType.DEPENDENCY, include_technical=False
        )
        debug_log(f"Web UI 模組導入失敗 [錯誤ID: {error_id}]: {e}")

        return {
            "command_logs": "",
            "interactive_feedback": user_error_msg,
            "images": [],
        }


@mcp.tool()
def get_system_info() -> str:
    """
    獲取系統環境資訊

    Returns:
        str: JSON 格式的系統資訊
    """
    is_remote = is_remote_environment()
    is_wsl = is_wsl_environment()

    # 檢測 AI 客戶端類型
    ai_client = os.getenv("MCP_AI_CLIENT", "").lower().strip()

    system_info = {
        "平台": sys.platform,
        "Python 版本": sys.version.split()[0],
        "WSL 環境": is_wsl,
        "遠端環境": is_remote,
        "介面類型": "Web UI",
        "AI 客戶端": ai_client if ai_client else "未指定",
        "Augment 模式": ai_client == "augment",
        "環境變數": {
            "MCP_AI_CLIENT": os.getenv("MCP_AI_CLIENT"),
            "MCP_DEBUG": os.getenv("MCP_DEBUG"),
            "MCP_WEB_HOST": os.getenv("MCP_WEB_HOST"),
            "MCP_WEB_PORT": os.getenv("MCP_WEB_PORT"),
            "MCP_DESKTOP_MODE": os.getenv("MCP_DESKTOP_MODE"),
            "MCP_LANGUAGE": os.getenv("MCP_LANGUAGE"),
            "SSH_CONNECTION": os.getenv("SSH_CONNECTION"),
            "SSH_CLIENT": os.getenv("SSH_CLIENT"),
            "DISPLAY": os.getenv("DISPLAY"),
            "VSCODE_INJECTION": os.getenv("VSCODE_INJECTION"),
            "SESSIONNAME": os.getenv("SESSIONNAME"),
            "WSL_DISTRO_NAME": os.getenv("WSL_DISTRO_NAME"),
            "WSL_INTEROP": os.getenv("WSL_INTEROP"),
            "WSLENV": os.getenv("WSLENV"),
        },
    }

    return json.dumps(system_info, ensure_ascii=False, indent=2)


# ===== 主程式入口 =====
def main():
    """主要入口點，用於套件執行
    收集用戶的互動回饋，支援文字和圖片
    此工具使用 Web UI 介面收集用戶回饋，支援智能環境檢測。

    用戶可以：
    1. 執行命令來驗證結果
    2. 提供文字回饋
    3. 上傳圖片作為回饋
    4. 查看 AI 的工作摘要

    調試模式：
    - 設置環境變數 MCP_DEBUG=true 可啟用詳細調試輸出
    - 生產環境建議關閉調試模式以避免輸出干擾


    """
    # 檢查是否啟用調試模式
    debug_enabled = os.getenv("MCP_DEBUG", "").lower() in ("true", "1", "yes", "on")

    # 檢查是否啟用桌面模式
    desktop_mode = os.getenv("MCP_DESKTOP_MODE", "").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )

    # AI 客戶端類型現在在 WebUIManager 初始化時讀取（與 MCP_WEB_PORT 處理方式完全一致）

    if debug_enabled:
        debug_log("🚀 啟動互動式回饋收集 MCP 服務器")
        debug_log(f"   服務器名稱: {SERVER_NAME}")
        debug_log(f"   版本: {__version__}")
        debug_log(f"   平台: {sys.platform}")
        debug_log(f"   編碼初始化: {'成功' if _encoding_initialized else '失敗'}")
        debug_log(f"   遠端環境: {is_remote_environment()}")
        debug_log(f"   WSL 環境: {is_wsl_environment()}")
        debug_log(f"   桌面模式: {'啟用' if desktop_mode else '禁用'}")
        debug_log("   介面類型: Web UI")
        debug_log("   AI 客戶端類型: 將在 WebUIManager 初始化時讀取")
        debug_log("   等待來自 AI 助手的調用...")
        debug_log("準備啟動 MCP 伺服器...")
        debug_log("調用 mcp.run()...")

    # 在 MCP 服务器启动前，读取并保存服务器配置
    global _startup_ai_client_type
    _startup_ai_client_type = os.getenv('MCP_AI_CLIENT', 'augment').lower().strip()

    # 打印启动配置到 stderr（不干扰 MCP 协议）
    print(f"[STARTUP_CHECK] MCP_AI_CLIENT = {os.getenv('MCP_AI_CLIENT')!r}", file=sys.stderr, flush=True)
    print(f"[STARTUP_CHECK] MCP_WEB_PORT = {os.getenv('MCP_WEB_PORT')!r}", file=sys.stderr, flush=True)
    print(f"[STARTUP_CHECK] 当前进程PID: {os.getpid()}", file=sys.stderr, flush=True)
    print(f"[STARTUP_CHECK] 服务器固定处理方式: {_startup_ai_client_type}", file=sys.stderr, flush=True)

    try:
        # 使用正確的 FastMCP API
        mcp.run()
    except KeyboardInterrupt:
        if debug_enabled:
            debug_log("收到中斷信號，正常退出")
        sys.exit(0)
    except Exception as e:
        if debug_enabled:
            debug_log(f"MCP 服務器啟動失敗: {e}")
            import traceback

            debug_log(f"詳細錯誤: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
