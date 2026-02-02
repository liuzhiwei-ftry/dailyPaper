from PySide6.QtCore import QThread, Signal
from config.app_config import global_config
import time
import sys
from volcenginesdkarkruntime import Ark


class GenerateReportThread(QThread):
    """日报生成线程（完全对齐附件逻辑，仅需ARK_API_KEY，流式生成+日志分离）"""
    text_signal = Signal(str)  # 仅传递AI生成的日报内容（流式逐块）
    log_signal = Signal(str)   # 仅传递执行日志（鉴权/调用/解析/状态）
    finish_signal = Signal()   # 生成完成/中断通用信号
    error_signal = Signal(str) # 错误弹窗信号（关键错误）

    def __init__(self, template_content: str, work_content: str):
        super().__init__()
        # 业务参数：模板+工作内容（去空格）
        self.template_content = template_content.strip()
        self.work_content = work_content.strip()
        # 线程控制：取消标记（线程安全）
        self._is_canceled = False
        # 火山方舟配置：仅读取ARK_API_KEY和模型名（对齐附件）
        self._ark_api_key = global_config.ark_api_key.strip()
        self._model_name = global_config.model_name.strip() or "doubao-seed-1-6-lite-251015"
        # 方舟客户端实例
        self._ark_client = None

    def cancel(self):
        """外部调用：触发生成中断，标记取消状态"""
        if not self._is_canceled:
            self._is_canceled = True
            self.log_signal.emit("🛑 接收到中断指令，正在终止模型请求...\n")

    def is_canceled(self) -> bool:
        """内部检测：是否被取消"""
        return self._is_canceled

    def _init_ark_client(self) -> bool:
        """初始化火山方舟客户端（仅需ARK_API_KEY，完全对齐附件逻辑），返回是否成功"""
        self.log_signal.emit(f"📦 开始初始化火山方舟客户端 | 目标模型：{self._model_name}\n")
        # 仅校验ARK_API_KEY（附件唯一鉴权要求）
        if not self._ark_api_key:
            self.log_signal.emit("❌ ARK_API_KEY未配置！请在【系统→配置】填写唯一鉴权密钥\n")
            return False
        # 按附件标准初始化客户端（base_url固定，不可修改）
        try:
            self._ark_client = Ark(
                base_url="https://ark.cn-beijing.volces.com/api/v3",  # 火山方舟华北区固定端点（附件同款）
                api_key=self._ark_api_key  # 仅需这一个鉴权字段（核心）
            )
            self.log_signal.emit("✅ 火山方舟客户端初始化成功（仅ARK_API_KEY鉴权通过）\n")
            return True
        except Exception as e:
            err_info = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            self.log_signal.emit(f"❌ 客户端初始化失败：{err_info} | 请检查ARK_API_KEY是否正确\n")
            return False

    def run(self):
        """核心执行逻辑：对齐附件SDK调用流程，流式生成+日志分离"""
        try:
            # 前置检测1：是否被提前取消
            if self.is_canceled():
                self._reset_state()
                return

            # 前置检测2：初始化方舟客户端（仅ARK_API_KEY鉴权）
            if not self._init_ark_client():
                self.error_signal.emit("火山方舟客户端初始化失败！请检查配置窗口的ARK_API_KEY")
                self._reset_state()
                return

            # 前置检测3：业务参数非空
            if not self.template_content:
                self.error_signal.emit("日报模板不能为空！请在【模版编辑】Tab填写内容")
                self.log_signal.emit("❌ 生成终止：日报模板内容为空\n")
                self._reset_state()
                return
            if not self.work_content:
                self.error_signal.emit("工作内容不能为空！请在【工作内容】Tab粘贴/输入")
                self.log_signal.emit("❌ 生成终止：当日工作内容为空\n")
                self._reset_state()
                return

            # 步骤1：拼接Prompt（模板+工作内容，纯文本格式，附件同款）
            self.log_signal.emit("📝 开始拼接Prompt，按模板+工作内容生成规范日报\n")
            prompt = f"""你是专业的职场工作日报生成助手，严格按照以下要求生成日报：
1. 仅输出最终的日报内容，不添加任何额外的解释、备注、提示语；
2. 完全保留我提供的日报模板的所有结构和格式（标题、分级、标点等）；
3. 将我的当日工作内容精准融入模板对应的模块，不遗漏任何关键信息；
4. 语言简洁正式、逻辑清晰，符合企业职场日报的书写规范；
5. 流式生成的内容要连续无重复，段落之间衔接自然。

我的日报模板：
{self.template_content}

我的当日工作内容：
{self.work_content}

请直接输出最终的日报内容，无需其他任何内容！"""
            time.sleep(0.3)  # 短暂延时，避免配置未实时同步
            if self.is_canceled():
                self._reset_state()
                return

            # 步骤2：调用模型（使用client.responses.create，完全对齐附件逻辑，核心修改）
            self.log_signal.emit(f"🚀 正在调用模型 {self._model_name} | 开启流式响应（附件同款SDK调用）\n")
            self.log_signal.emit("📥 开始接收流式内容，结果将实时输出到【生成结果】Tab...\n")
            try:
                stream_resp = self._ark_client.responses.create(
                    model=self._model_name,  # 目标模型ID
                    input=prompt,            # 纯文本Prompt（附件同款参数）
                    temperature=0.3,         # 低温度保证模板结构不偏移（附件推荐值）
                    stream=True,             # 核心：开启流式生成
                    thinking={"type": "disabled"},  # 关闭思考过程，避免无关内容（附件同款）
                )
            except Exception as req_e:
                err_info = str(req_e)[:150] + "..." if len(str(req_e)) > 150 else str(req_e)
                err_msg = f"模型调用失败：{err_info}"
                self.log_signal.emit(f"❌ {err_msg} | 请检查模型权限/ARK_API_KEY/网络\n")
                self.error_signal.emit(err_msg + "\n建议：1. 检查模型是否开通权限 2. 验证ARK_API_KEY有效性 3. 确保网络能访问方舟平台")
                self._reset_state()
                return

            # 步骤3：解析流式响应（复用附件的兼容逻辑，同时支持chunk.text和chunk.output，核心）
            for chunk in stream_resp:
                # 实时检测中断，立即终止循环
                if self.is_canceled():
                    self.text_signal.emit("\n\n🛑 日报生成已被手动中断，内容未完成")
                    self.log_signal.emit("🛑 流式响应终止 | 模型请求已关闭\n")
                    self._reset_state()
                    return
                # 解析单块内容，过滤空值（附件同款解析逻辑）
                chunk_text = self._parse_stream_chunk(chunk)
                if chunk_text:
                    self.text_signal.emit(chunk_text)  # 仅输出纯生成内容到结果域
                    time.sleep(0.03)  # 微调输出速度，避免刷屏

            # 步骤4：生成完成校验（未被中断则触发完成）
            if not self.is_canceled():
                self.log_signal.emit(f"\n✅ 流式生成完成 | 模型 {self._model_name} 调用成功（附件同款SDK）！\n")
                self.log_signal.emit("📜 生成结果已就绪，可直接复制/编辑/保存到历史记录\n")
                self.finish_signal.emit()

        except Exception as e:
            # 非中断导致的全局异常，捕获并反馈
            if not self.is_canceled():
                err_info = str(sys.exc_info()[-1])[:150] + "..." if len(str(sys.exc_info()[-1])) > 150 else str(sys.exc_info()[-1])
                err_msg = f"生成过程异常：{err_info}"
                self.log_signal.emit(f"❌ 全局异常：{err_msg}\n")
                self.error_signal.emit(err_msg)
            self._reset_state()

    def _parse_stream_chunk(self, chunk) -> str:
        """解析流式响应块（完全复用附件的兼容逻辑，支持新旧SDK版本）"""
        try:
            # 适配旧版SDK：直接从chunk.text获取内容（附件优先逻辑）
            if hasattr(chunk, 'text') and chunk.text and chunk.text.strip():
                return chunk.text.strip()
            # 适配新版SDK：从嵌套的chunk.output获取内容（附件兜底逻辑）
            elif hasattr(chunk, 'output') and chunk.output:
                for output in chunk.output:
                    if hasattr(output, 'content') and output.content:
                        for content in output.content:
                            if hasattr(content, 'text') and content.text.strip():
                                return content.text.strip()
            # 无有效内容返回空
            return ""
        except Exception as e:
            self.log_signal.emit(f"⚠️  跳过无效响应块：{str(e)[:50]}...\n")
            return ""

    def _reset_state(self):
        """重置线程状态，触发完成信号（让主窗口复位按钮/加载状态）"""
        self._is_canceled = False
        self.finish_signal.emit()