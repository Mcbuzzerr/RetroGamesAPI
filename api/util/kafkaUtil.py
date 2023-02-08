import asyncio
import confluent_kafka
from confluent_kafka import KafkaException, Consumer, Producer

# Producer Class
class producer:
    def __init__(
        self, configs: dict = {"bootstrap.servers": "kafka-simple-broker:9092"}
    ):
        if configs.get("bootstrap.servers") is None:
            config = {
                "bootstrap.servers": "kafka-simple-broker:9092",
            }
        else:
            config = configs
        self.p = Producer(config)

    def produce(self, topic, value, debug=False):
        if debug:
            DTicket(prompt={topic, value}, header="Producer Log")
        self.p.produce(topic, value, callback=self.receipt)
        self.p.flush()

    def receipt(self, err, msg):
        if err is not None:
            print("Failed to deliver message: {0}: {1}".format(msg.value(), err.str()))
        else:
            message = "Produced message on topic {0} with value of {1}".format(
                msg.topic(), msg.value().decode("utf-8")
            )
            print(message)


# Consumer Class
class consumer:
    def __init__(
        self,
        configs: dict = {"bootstrap.servers": "localhost:9092", "doAutoStart": False},
    ):
        if configs.get("bootstrap.servers") is None:
            config = {
                "bootstrap.servers": "localhost:9092",
            }
        else:
            config = configs

        self.c = Consumer(config)
        print("Consumer created")

        print("Available topics: ", self.c.list_topics().topics)
        self.c.subscribe(["accounts"])
        self.loop: bool = True
        if configs.get("doAutoStart") is not None:
            self.consumeLoop()

    # Upload messages to mongoDB
    def consumeLoop(self):
        while self.loop:
            msg = self.c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Error: {}".format(msg.error()))
                continue
            data = msg.value().decode("utf-8")
            print("Received message: {}".format(data))
        self.c.close()

    def setLoop(self, loop: bool):
        self.loop = loop


def DTicket(prompt, header="", delineator="=", width=40):
    for i in range(width):
        if i > 2 and i < (len(header) + 3):
            print(header[i - 3], end="")
        else:
            print(delineator, end="")
    print()
    if type(prompt) == str:
        print(prompt)
    elif type(prompt) == dict:
        dicto: dict = prompt
        for key in dicto.keys():
            print(key, dicto.get(key), sep=": ")
    elif type(prompt) == list:
        num = 0
        for i in prompt:
            num += 1
            print(num, i, sep=". ")

    for i in range(width):
        print(delineator, end="")
    print()
