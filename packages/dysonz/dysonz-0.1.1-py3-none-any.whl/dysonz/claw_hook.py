from .datas import Hook, Order

class EvenHook(Hook):
    def try_grab(self, item):
        try:
            assert isinstance(item,int)
        except AssertionError as e:
            return False

        return int(item) % 2 == 0

    def on_grab(self, item):
        print(f"[EvenHook] 抓取 {item}")


class BigHook(Hook):
    def try_grab(self, item):
        try:
            assert isinstance(item,int)
        except AssertionError as e:
            return False
        
        return int(item) > 10

    def on_grab(self, item):
        print(f"[BigHook] 抓取 {item}")




class PriceHook(Hook):
    def try_grab(self, obj):
        return isinstance(obj, Order) and obj.price > 100

    def on_grab(self, obj):
        print(f"抓取订单 {obj.order_id}")
