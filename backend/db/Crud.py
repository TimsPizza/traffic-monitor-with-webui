import logging
from typing import List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from core.services import ENV_CONFIG
from packet.Packet import ProcessedPacket

class PacketDB:
  def __init__(self, uri: str = ENV_CONFIG.database_uri, db_name: str = "traffic_analyzer"):
    self.client = MongoClient(uri)
    
    self.db: Database = self.client[db_name]
    self.packets_collection: Collection = self.db.packets
    self.logger = logging.getLogger(self.__class__.__name__)
    
    # Create indexes for better query performance
    self.packets_collection.create_index([("timestamp", -1)])
    self.packets_collection.create_index([("source_ip", 1)])
    self.packets_collection.create_index([("protocol", 1)])

  def insert_packet(self, packet: ProcessedPacket) -> bool:
    """Insert a single processed packet into the database"""
    try:
      packet_dict = {
        "timestamp": packet.timestamp,
        "layer": packet.layer,
        "source_ip": packet.source_ip,
        "src_port": packet.src_port,
        "dst_port": packet.dst_port,
        "protocol": packet.protocol,
        "length": packet.length
      }
      result = self.packets_collection.insert_one(packet_dict)
      return bool(result.inserted_id)
    except Exception as e:
      self.logger.error(f"Error inserting packet: {e}")
      return False

  def insert_many_packets(self, packets: List[ProcessedPacket]) -> int:
    """Insert multiple processed packets into the database"""
    try:
      packet_dicts = [
        {
          "timestamp": packet.timestamp,
          "layer": packet.layer,
          "source_ip": packet.source_ip,
          "src_port": packet.src_port,
          "dst_port": packet.dst_port,
          "protocol": packet.protocol
        }
        for packet in packets
      ]
      result = self.packets_collection.insert_many(packet_dicts)
      return len(result.inserted_ids)
    except Exception as e:
      self.logger.error(f"Error inserting multiple packets: {e}")
      return 0

  def find_packets_by_ip(self, ip_address: str) -> List[ProcessedPacket]:
    """Find all packets from a specific IP address"""
    try:
      cursor = self.packets_collection.find({"source_ip": ip_address})
      return [self._create_packet_from_dict(doc) for doc in cursor]
    except Exception as e:
      self.logger.error(f"Error finding packets by IP: {e}")
      return []

  def find_packets_by_protocol(self, protocol: str) -> List[ProcessedPacket]:
    """Find all packets with a specific protocol"""
    try:
      cursor = self.packets_collection.find({"protocol": protocol})
      return [self._create_packet_from_dict(doc) for doc in cursor]
    except Exception as e:
      self.logger.error(f"Error finding packets by protocol: {e}")
      return []

  def find_packets_by_timerange(self, start_time: float, end_time: float) -> List[ProcessedPacket]:
    """Find all packets within a specific time range"""
    try:
      cursor = self.packets_collection.find({
        "timestamp": {
          "$gte": start_time,
          "$lte": end_time
        }
      })
      return [self._create_packet_from_dict(doc) for doc in cursor]
    except Exception as e:
      self.logger.error(f"Error finding packets by time range: {e}")
      return []

  def delete_packets_before(self, timestamp: float) -> int:
    """Delete all packets before a specific timestamp"""
    try:
      result = self.packets_collection.delete_many({"timestamp": {"$lt": timestamp}})
      return result.deleted_count
    except Exception as e:
      self.logger.error(f"Error deleting old packets: {e}")
      return 0

  @staticmethod
  def _create_packet_from_dict(doc: dict) -> ProcessedPacket:
    """Convert a MongoDB document to a ProcessedPacket object"""
    return ProcessedPacket(
      timestamp=doc.get("timestamp", -1),
      layer=doc.get("layer", ""),
      source_ip=doc.get("source_ip", ""),
      src_port=doc.get("src_port", -1),
      dst_port=doc.get("dst_port", -1),
      protocol=doc.get("protocol", "")
    )

  def close(self):
    """Close the MongoDB connection"""
    self.client.close()


MONGO_DB = PacketDB()