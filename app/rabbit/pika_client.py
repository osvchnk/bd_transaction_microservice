import json
import time

import pika
from pydantic import BaseModel

from app.config import RABBIT_HOST, RABBIT_PORT, RABBIT_EXCHANGE, RABBIT_ROUTING_KEY


class MyModel(BaseModel):
    id: int
    name: str


class PikaPublisher:
    def __init__(self,
                 exchange_name: str = RABBIT_EXCHANGE,
                 routing_key: str = RABBIT_ROUTING_KEY
                 ):
        self.conn_params = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
        self.connection = pika.BlockingConnection(self.conn_params)
        self.channel = self.connection.channel()
        self.exchange_name = exchange_name
        self.routing_key = routing_key

        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.connection.close()

    def send_message(self, message: dict):
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.routing_key,
            body=json.dumps(message).encode('utf-8')
        )


if __name__ == "__main__":
    trs = []
    for tr in trs:
        with PikaPublisher() as client:
            client.send_message({"tr_hash": tr})
            time.sleep(1)

