#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kafka 队列操作的抽象和实现（基于 confluent-kafka）
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class KafkaConfig:
    """
    Kafka 配置类，包含生产者和消费者的常用配置参数
    """
    # 基础配置
    bootstrap_servers: str = "localhost:9092"
    
    # 生产者配置
    client_id: str = "xcmap-producer"
    
    # 消费者配置
    group_id: str = "xcmap-consumer-group"
    auto_offset_reset: str = "earliest"
    
    # 自定义生产者和消费者配置
    producer_extra_config: Dict[str, Any] = field(default_factory=dict)
    consumer_extra_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_producer_config(self) -> Dict[str, Any]:
        """
        获取生产者配置
        
        Returns:
            Dict: 完整的生产者配置字典
        """
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': self.client_id
        }
        config.update(self.producer_extra_config)
        return config
    
    def get_consumer_config(self) -> Dict[str, Any]:
        """
        获取消费者配置
        
        Returns:
            Dict: 完整的消费者配置字典
        """
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': self.auto_offset_reset
        }
        config.update(self.consumer_extra_config)
        return config


class KafkaQueue(ABC):
    """
    Kafka 队列操作的抽象基类
    """

    @abstractmethod
    def send_message(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """
        发送消息到指定主题

        Args:
            topic: 主题名称
            value: 消息内容
            key: 消息键

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    def consume_messages(self, topics: List[str], message_handler: Callable[[Any], None],
                         timeout: float = 1.0) -> None:
        """
        消费指定主题的消息

        Args:
            topics: 主题列表
            message_handler: 消息处理函数
            timeout: 超时时间（秒）
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        关闭连接
        """
        pass


class ConfluentKafkaQueue(KafkaQueue):
    """
    基于 confluent-kafka 库的 Kafka 队列实现
    """

    def __init__(self, config: Optional[KafkaConfig] = None, 
                 producer_config: Optional[Dict] = None, 
                 consumer_config: Optional[Dict] = None):
        """
        初始化 Kafka 队列

        Args:
            config: Kafka配置对象
            producer_config: 生产者配置（会覆盖config中的配置）
            consumer_config: 消费者配置（会覆盖config中的配置）
        """
        try:
            from confluent_kafka import Producer, Consumer
            self.kafka_available = True
        except ImportError:
            logger.warning("confluent-kafka 未安装，Kafka 功能将不可用")
            self.kafka_available = False
            return

        # 使用传入的配置对象或创建默认配置
        self.config = config or KafkaConfig()
        
        # 合并配置，参数传入的配置优先级更高
        self.producer_config = self.config.get_producer_config()
        if producer_config:
            self.producer_config.update(producer_config)
            
        self.consumer_config = self.config.get_consumer_config()
        if consumer_config:
            self.consumer_config.update(consumer_config)

        self.producer: Optional[Producer] = None
        self.consumer: Optional[Consumer] = None

    def _get_producer(self):
        """
        获取或创建生产者实例

        Returns:
            Producer: 生产者实例
        """
        if not self.kafka_available:
            raise RuntimeError("confluent-kafka 未安装，无法创建生产者")

        if self.producer is None:
            from confluent_kafka import Producer
            self.producer = Producer(self.producer_config)
        return self.producer

    def _get_consumer(self):
        """
        获取或创建消费者实例

        Returns:
            Consumer: 消费者实例
        """
        if not self.kafka_available:
            raise RuntimeError("confluent-kafka 未安装，无法创建消费者")

        if self.consumer is None:
            from confluent_kafka import Consumer
            self.consumer = Consumer(self.consumer_config)
        return self.consumer

    def send_message(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """
        发送消息到指定主题

        Args:
            topic: 主题名称
            value: 消息内容（可以是字符串、字典等）
            key: 消息键

        Returns:
            bool: 发送是否成功
        """
        if not self.kafka_available:
            logger.error("Kafka 不可用，请检查 confluent-kafka 是否正确安装")
            return False

        try:
            producer = self._get_producer()

            # 序列化消息内容
            if isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, (str, bytes)):
                value = str(value)

            # 确保消息内容是字节类型
            if isinstance(value, str):
                value = value.encode('utf-8')

            # 发送消息
            producer.produce(topic, key=key, value=value)
            producer.flush()
            return True
        except Exception as e:
            logger.error(f"发送消息到主题 {topic} 失败: {e}")
            return False

    def consume_messages(self, topics: List[str], message_handler: Callable[[Any], None],
                         timeout: float = 1.0) -> None:
        """
        消费指定主题的消息

        Args:
            topics: 主题列表
            message_handler: 消息处理函数
            timeout: 超时时间（秒）
        """
        if not self.kafka_available:
            logger.error("Kafka 不可用，请检查 confluent-kafka 是否正确安装")
            return

        try:
            consumer = self._get_consumer()
            consumer.subscribe(topics)

            while True:
                msg = consumer.poll(timeout)
                if msg is None:
                    continue

                if msg.error():
                    logger.error(f"消费者错误: {msg.error()}")
                    continue

                try:
                    message_handler(msg)
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        except KeyboardInterrupt:
            logger.info("消费者被中断")
        except Exception as e:
            logger.error(f"消费消息时出错: {e}")
        finally:
            self.close()

    def close(self) -> None:
        """
        关闭 Kafka 连接
        """
        if not self.kafka_available:
            return

        if self.producer:
            self.producer.flush()
            self.producer = None

        if self.consumer:
            self.consumer.close()
            self.consumer = None


def create_kafka_queue(config: Optional[KafkaConfig] = None,
                       producer_config: Optional[Dict] = None,
                       consumer_config: Optional[Dict] = None) -> KafkaQueue:
    """
    创建 Kafka 队列实例

    Args:
        config: Kafka配置对象
        producer_config: 生产者配置（会覆盖config中的配置）
        consumer_config: 消费者配置（会覆盖config中的配置）

    Returns:
        KafkaQueue: Kafka 队列实例
    """
    return ConfluentKafkaQueue(config, producer_config, consumer_config)


def default_message_handler(msg) -> None:
    """
    默认消息处理函数

    Args:
        msg: Kafka 消息对象
    """
    try:
        # 尝试解析消息
        topic = msg.topic() if hasattr(msg, 'topic') else 'unknown'
        partition = msg.partition() if hasattr(msg, 'partition') else 'unknown'
        offset = msg.offset() if hasattr(msg, 'offset') else 'unknown'
        key = msg.key().decode('utf-8') if msg.key() else None
        
        # 尝试解析 JSON 消息
        try:
            value = json.loads(msg.value().decode('utf-8'))
        except (json.JSONDecodeError, AttributeError):
            value = msg.value().decode('utf-8') if msg.value() else None
            
        logger.info(f"收到消息 - 主题: {topic}, 分区: {partition}, "
                    f"偏移量: {offset}, 键: {key}, 值: {value}")
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")


def main(topic="test_topic"):
    """
    主函数，用于测试 Kafka 队列功能
    
    Args:
        topic: 要发送和消费的主题名称
    """
    import time
    import threading
    
    # 使用配置类配置 Kafka
    kafka_config = KafkaConfig(
        bootstrap_servers='10.1.253.16:9092',
        group_id='test_group_' + str(int(time.time())),  # 使用时间戳确保每次都是新的消费者组
        auto_offset_reset='earliest'
    )
    
    # 创建 Kafka 队列实例
    kafka_queue = create_kafka_queue(config=kafka_config)
    
    if not kafka_queue.kafka_available:
        print("错误: confluent-kafka 未安装或不可用")
        print("请运行以下命令安装:")
        print("  pip install confluent-kafka")
        return
    
    # 测试发送消息
    print(f"正在测试发送消息到主题: {topic}...")
    test_message = {
        "timestamp": time.time(),
        "message": "这是一条测试消息",
        "sender": "test_producer"
    }
    
    success = kafka_queue.send_message(topic, test_message, "test_key")
    if success:
        print("消息发送成功!")
    else:
        print("消息发送失败!")
        return
    
    # 关闭生产者，确保消息已发送
    kafka_queue.close()
    
    # 等待一小段时间确保消息已被服务器接收
    time.sleep(1)
    
    # 测试消费消息（只消费5秒钟）
    print(f"正在测试消费主题 {topic} 的消息...")
    print("将在5秒后自动停止消费")
    
    # 使用线程运行消费者，避免阻塞主线程
    consumer_result = {"running": True}
    
    def consume_worker():
        try:
            # 创建新的消费者实例
            consumer_config = KafkaConfig(
                bootstrap_servers='10.1.253.16:9092',
                group_id='test_consumer_' + str(int(time.time())),  # 新的消费者组ID
                auto_offset_reset='earliest'
            )
            consumer_queue = create_kafka_queue(config=consumer_config)
            
            # 存储消费者引用以便主线程可以关闭它
            consumer_result["consumer"] = consumer_queue
            
            consumer_queue.consume_messages([topic], default_message_handler, timeout=1.0)
        except Exception as e:
            print(f"消费测试出错: {e}")
        finally:
            consumer_result["running"] = False
            print("\n消费测试结束")
    
    # 启动消费者线程
    consumer_thread = threading.Thread(target=consume_worker, daemon=True)
    consumer_thread.start()
    
    # 等待5秒后停止消费
    time.sleep(5)
    
    # 停止消费者
    if "consumer" in consumer_result:
        consumer_result["consumer"].close()
    
    print("5秒钟已过，停止消费...")
    
    # 等待消费者线程结束
    consumer_thread.join(timeout=1)


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "test_topic"
    main(topic)