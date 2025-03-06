from logging import Logger
from typing import List
from packet.PacketAnalyzer import AnalyzerSingleton
from core.config import ENV_CONFIG
from models.Filter import CaptureFilterRecord
from packet.utils.BpfUtils import BPFUtils
from service.ConfigService import ConfigService


class CaptureService:
    def __init__(self):
        self.config_service = ConfigService()
        self.analyzer = AnalyzerSingleton.get_instance()
        self.logger = Logger(self.__class__.__name__, level=ENV_CONFIG.log_level)

    def start_capture(self) -> bool:
        """启动抓包分析器 (Start packet analyzer)"""
        try:
            # 从配置文件加载过滤器 (Load filters from config file)
            filters = self.config_service.get_all_filter()
            if filters.filters:
                bpf_expression = BPFUtils.build_filter_expression(filters.filters)
                if bpf_expression:
                    self.analyzer.set_filter(bpf_expression)

            # 从配置文件加载规则 (Load rules from config file)
            rules = self.config_service.get_all_protocol_port_mapping_rules()
            if rules.rules:
                self.analyzer.set_rules(rules.rules)

            # 启动分析器 (Start analyzer)
            self.analyzer.start()
            return True
        except Exception as e:
            self.logger.error(f"Error starting capture: {e}")
            return False

    def stop_capture(self) -> bool:
        """停止抓包分析器 (Stop packet analyzer)"""
        try:
            self.analyzer.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping capture: {e}")
            return False

    def is_capturing(self) -> bool:
        """检查分析器是否正在运行 (Check if analyzer is running)"""
        return self.analyzer.is_running
