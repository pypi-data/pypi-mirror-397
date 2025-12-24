class Hook:
    def try_grab(self, item) -> bool:
        raise NotImplementedError

    def on_grab(self, item):
        pass


class Order:
    def __init__(self, order_id, price):
        self.order_id = order_id
        self.price = price

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["order_id"], d["price"])
