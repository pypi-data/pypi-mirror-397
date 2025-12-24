# 工作台

import time
from collections import defaultdict
from queue import Queue


class ProductLot:
    def __init__(self, product: str, amount: int, cost: dict):
        self.product = product
        self.amount = amount
        self.cost = cost
        self.timestamp = time.time()

    def __repr__(self):
        return f"<{self.product} x{self.amount} cost={self.cost}>"


class Workbench:
    def __init__(self,
                 total_capacity: int,
                 resource_limits: dict,
                 recipes: list,
                 cleanup_timeout: float):
        """
        total_capacity: 仓储总容量
        resource_limits: 单种资源最大容量
        recipes: 配方列表
        cleanup_timeout: 资源最长堆积时间（秒）
        """
        self.total_capacity = total_capacity
        self.resource_limits = resource_limits
        self.recipes = recipes
        self.cleanup_timeout = cleanup_timeout

        self.resources = defaultdict(int)
        self.last_used_time = {}
        self.output_queue = Queue()

    # ---------- 资源相关 ----------
    def total_amount(self):
        return sum(self.resources.values())

    def add_resource(self, res_type: str, amount: int) -> bool:
        if self.total_amount() + amount > self.total_capacity:
            return False
        if res_type in self.resource_limits:
            if self.resources[res_type] + amount > self.resource_limits[res_type]:
                return False

        self.resources[res_type] += amount
        self.last_used_time[res_type] = time.time()
        return True

    def has_resources(self, needs: dict) -> bool:
        return all(self.resources[r] >= n for r, n in needs.items())

    def consume_resources(self, needs: dict):
        for r, n in needs.items():
            self.resources[r] -= n
            self.last_used_time[r] = time.time()

    # ---------- 生产逻辑 ----------
    def produce_once(self) -> bool:
        for recipe in self.recipes:
            if self.has_resources(recipe["inputs"]):

                # 记录成本
                cost = dict(recipe["inputs"])

                # 消耗原料
                self.consume_resources(recipe["inputs"])

                # 生成成品包
                for product, count in recipe["outputs"].items():
                    lot = ProductLot(product, count, cost)
                    self.output_queue.put(lot)

                return True
        return False

    def produce_until_exhausted(self):
        """
        连续生产，直到所有配方均无法满足
        """
        while self.produce_once():
            pass

    def dispatch(self, max_items: int = None):
        """
        将成品发送到外部系统
        返回发送出去的成品列表
        """
        sent = []
        while not self.output_queue.empty():
            if max_items is not None and len(sent) >= max_items:
                break
            sent.append(self.output_queue.get())
        return sent



    # ---------- 清理逻辑 ----------
    def cleanup(self):
        now = time.time()
        to_clear = []
        for r, t in self.last_used_time.items():
            if now - t > self.cleanup_timeout:
                to_clear.append(r)

        for r in to_clear:
            del self.resources[r]
            del self.last_used_time[r]

    # ---------- 状态查看 ----------
    def status(self):
        return {
            "resources": dict(self.resources),
            "output_count": self.output_queue.qsize()
        }



