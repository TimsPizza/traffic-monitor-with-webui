from packet import PacketAnalyzer

class AnalyzerSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PacketAnalyzer(
                buffer_min_size=256,
                buffer_max_size=8192,
                consumer_max_workers=4,
                consumer_batch_size=256,
                capture_interface="eth0",
            )
        return cls._instance