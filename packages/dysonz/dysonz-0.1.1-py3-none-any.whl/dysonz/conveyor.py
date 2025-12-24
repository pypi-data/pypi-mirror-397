# 传送带

import json
from typing import List
from .datas import Hook

class Serializer:
    _registry = {}

    @classmethod
    def register(cls, name, cls_type):
        cls._registry[name] = cls_type

    @classmethod
    def dumps(cls, obj) -> bytes:
        # 普通类型（str / int / list / dict）
        if isinstance(obj, (str, int, float, list, dict)):
            payload = {
                "__type__": "builtin",
                "data": obj
            }
        else:
            payload = {
                "__type__": obj.__class__.__name__,
                "data": obj.to_dict()
            }
        return json.dumps(payload).encode("utf-8")

    @classmethod
    def loads(cls, raw: bytes):
        payload = json.loads(raw.decode("utf-8"))
        t = payload["__type__"]
        data = payload["data"]

        if t == "builtin":
            return data

        if t not in cls._registry:
            raise ValueError(f"未注册的对象类型: {t}")

        return cls._registry[t].from_dict(data)


class Conveyor:
    def __init__(self, redis_client, queue_key: str, hooks: List[Hook]):
        self.r = redis_client
        self.queue_key = queue_key
        self.hooks = hooks
        with open("conveyor_utils/grab.lua", "r") as f:
            self.lua = self.r.register_script(f.read())

    def push(self, obj):
        raw = Serializer.dumps(obj)
        self.r.lpush(self.queue_key, raw)

    def process_tail(self):
        raw = self.r.lindex(self.queue_key, -1)
        if raw is None:
            return

        item = Serializer.loads(raw)

        decisions = []
        for hook in self.hooks:
            decisions.append("1" if hook.try_grab(item) else "0")

        result = self.lua(
            keys=[self.queue_key],
            args=decisions
        )

        if result:
            raw_item, hook_index = result
            obj = Serializer.loads(raw_item)
            self.hooks[int(hook_index) - 1].on_grab(obj)
