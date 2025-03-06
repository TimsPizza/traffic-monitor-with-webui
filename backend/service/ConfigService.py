from collections import Counter
from logging import Logger
from typing import List, Type, Tuple, Optional, Dict, Any
from packet.PacketAnalyzer import AnalyzerSingleton
from core.config import ENV_CONFIG
import netifaces
import yaml
import os
from models.Dtos import (
    FilterAll,
    FullPacket,
    NetworkInterfaces,
    NetworkStats,
    PaginatedResponse,
    ProtocolDistributionItem,
    ProtocolPortMappingRuleRecord,
    ProtocolPortMappingRulesAll,
    TimeRange,
    TopSourceIP,
    ProtocolDistribution,
    TrafficSummary,
    TimeSeriesData,
)
from models.Filter import CaptureFilterRecord
from packet.utils.BpfUtils import BPFUtils

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


class ConfigService:
    def __init__(self):
        self.analyzer = AnalyzerSingleton.get_instance()
        self.logger = Logger(self.__class__.__name__, level=ENV_CONFIG.log_level)

    def _load_config(self) -> Dict:
        """加载配置文件 (Load configuration file)"""
        try:
            if not os.path.exists(CONFIG_PATH):
                return {"filters": [], "rules": []}
            with open(CONFIG_PATH, "r") as f:
                return yaml.safe_load(f) or {"filters": [], "rules": []}
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {"filters": [], "rules": []}

    def _save_config(self, config: Dict) -> bool:
        """保存配置文件 (Save configuration file)"""
        try:
            with open(CONFIG_PATH, "w") as f:
                yaml.safe_dump(
                    config,
                    f,
                    default_flow_style=True,
                    allow_unicode=True,
                )
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def get_all_filter(self) -> FilterAll:
        """获取所有过滤器规则 (Get all filter rules)"""
        try:
            config = self._load_config()
            filters = [CaptureFilterRecord(**f) for f in config.get("filters", [])]
            return FilterAll(filters=filters)
        except Exception as e:
            self.logger.error(f"Error getting filters: {e}")
            return FilterAll(filters=[])

    def add_filter(
        self, filter_records: List[CaptureFilterRecord]
    ) -> List[CaptureFilterRecord]:
        """设置新的过滤器规则 (Set new filter rules)"""
        try:
            # 构建并设置过滤器表达式 (Build and set filter expression)
            bpf_expression = BPFUtils.build_filter_expression(filter_records)
            if not self.analyzer.set_filter(bpf_expression):
                return []

            # 保存到配置文件 (Save to config file)
            config = self._load_config()
            config["filters"] = [f.model_dump() for f in filter_records]
            if not self._save_config(config):
                return []

            return filter_records
        except Exception as e:
            self.logger.error(f"Error adding filters: {e}")
            return []

    def get_all_protocol_port_mapping_rules(self) -> ProtocolPortMappingRulesAll:
        """获取所有端口映射规则 (Get all port mapping rules)"""
        try:
            config = self._load_config()
            rules_obj = config.get("rules", [])
            rules = [
                ProtocolPortMappingRuleRecord(ports=r["ports"], protocol=r["protocol"])
                for r in rules_obj
            ]
            return ProtocolPortMappingRulesAll(rules=rules)
        except Exception as e:
            self.logger.error(f"Error getting rules: {e}")
            return ProtocolPortMappingRulesAll(rules=[])

    def add_rule(self, rule: ProtocolPortMappingRuleRecord) -> bool:
        """添加新的端口映射规则 (Add new port mapping rule)"""
        try:
            self.logger.info(f"Adding rule: {rule}")
            config = self._load_config()
            rules: List[ProtocolPortMappingRuleRecord] = config.get("rules", [])
            if rule.protocol not in [r["protocol"] for r in rules]:
                rules.append(rule.model_dump())
            else:
                for r in rules:
                    if r["protocol"] != rule.protocol:
                        continue
                    r["ports"] = list(set(rule.ports))
                    break
            config["rules"] = rules

            # 保存到配置文件 (Save to config file)
            if not self._save_config(config):
                return False

            # 更新分析器 (Update analyzer)
            return self.analyzer.set_rules(
                [
                    ProtocolPortMappingRuleRecord(
                        ports=r["ports"], protocol=r["protocol"]
                    )
                    for r in rules
                ]
            )
        except Exception as e:
            self.logger.error(f"Error adding rule: {e}")
            return False

    def remove_rule(self, rule: ProtocolPortMappingRuleRecord) -> bool:
        """移除指定的端口映射规则 (Remove specified port mapping rule)"""
        try:
            self.logger.info(f"Removing rule: {rule}")
            config = self._load_config()
            rules: List[ProtocolPortMappingRuleRecord] = config.get("rules", [])

            # 删除规则 (Remove rule)
            for r in rules:
                if r["protocol"] == rule.protocol:
                    if ConfigService.are_elements_identical(r["ports"], rule.ports):
                        rules.remove(r)
                        break
                    else:
                        r["ports"] = list(set(r["ports"]) - set(rule.ports))
                        break
            config["rules"] = rules

            # 保存到配置文件 (Save to config file)
            if not self._save_config(config):
                return False

            # 更新分析器 (Update analyzer)
            rules_obj = [
                ProtocolPortMappingRuleRecord(ports=r["ports"], protocol=r["protocol"])
                for r in rules
            ]
            return self.analyzer.set_rules(rules_obj)
        except Exception as e:
            self.logger.error(f"Error removing rule: {e}")
            return False

    def get_all_net_interfaces(self) -> NetworkInterfaces:
        """获取所有网络接口 (Get all network interfaces)"""
        availables = netifaces.interfaces()
        selected = self.analyzer.get_active_interface()
        return NetworkInterfaces(interfaces=availables, selected=selected)

    def set_net_interface(self, interface: str) -> bool:
        """设置网络接口 (Set network interface)"""
        try:
            self.analyzer._packet_producer.set_interface(interface)
            return True
        except Exception as e:
            self.logger.error(f"Error setting interface: {e}")
            return False

    @staticmethod
    def are_elements_identical(arr1, arr2):
        if len(arr1) != len(arr2):
            return False

        return Counter(arr1) == Counter(arr2)


CONFIG_SERVICE = ConfigService()
