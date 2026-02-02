from volcenginesdkarkruntime import Ark
from config.app_config import global_config

class ArkAIClient:
    """火山方舟AI客户端封装"""
    _instance = None  # 单例

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """初始化客户端（从配置读取API_KEY）"""
        self.client = Ark(
            base_url='https://ark.cn-beijing.volces.com/api/v3',
            api_key=global_config.ark_api_key,
        )
        self.model_id = global_config.model_id

    def refresh_client(self):
        """刷新客户端（配置变更后调用）"""
        self._init_client()

    def generate_report_stream(self, template_content: str, work_content: str):
        """流式生成日报（返回生成器）"""
        prompt = f"{template_content}\n\n我提供的当日工作内容：{self._clean_content(work_content)}"
        stream_resp = self.client.responses.create(
            model=self.model_id,
            input=prompt,
            temperature=0.3,
            stream=True,
            thinking={"type": "disabled"},
        )
        return self._parse_stream_resp(stream_resp)

    def _clean_content(self, content: str) -> str:
        """清理内容（去除多余空白）"""
        return content.strip()

    def _parse_stream_resp(self, stream_resp):
        """解析流式响应（兼容新旧SDK）"""
        for chunk in stream_resp:
            # 旧版本
            if hasattr(chunk, 'text') and chunk.text and chunk.text.strip():
                yield chunk.text.strip()
            # 新版本
            elif hasattr(chunk, 'output') and chunk.output:
                for output in chunk.output:
                    if hasattr(output, 'content') and output.content:
                        for content in output.content:
                            if hasattr(content, 'text') and content.text.strip():
                                yield content.text.strip()