import time
import redis
from dysonz.datas import Order
from dysonz.conveyor import Conveyor, Serializer
from dysonz.claw_hook import EvenHook, BigHook, PriceHook


# 注册
# Serializer.register("Order", Order)


r = redis.Redis(host="127.0.0.1", port=6379,db=12, decode_responses=False)
print("redis ping:", r.ping())

# ⚠️ 为了防止历史脏数据，先清空
r.delete("conveyor:queue")

conveyor = Conveyor(
    redis_client=r,
    queue_key="conveyor:queue",
    hooks=[EvenHook(), BigHook()]
)


print("pushing items...")
for i in range(10, 20):
    x = Order(134,223+i)
    conveyor.push(i)
    # conveyor.push(x)
    print(f"pushed {i}")

print("start processing...\n")

while True:
    conveyor.process_tail()
    time.sleep(1)
