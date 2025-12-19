# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  redis-helper
# FileName:     client.py
# Description:  redis客户端模块
# Author:       ASUS
# CreateDate:   2025/12/16
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import json
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Any, Union, Optional, Awaitable, Literal, Iterable, List

standard_date_format = "%Y-%m-%d %H:%M:%S"


class AsyncRedisHelper:
    def __init__(self, **kwargs):
        self._r = redis.Redis(**kwargs)

    @property
    def redis(self) -> redis.Redis:
        return self._r

    async def set(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None, **kwargs):
        """
        写入redis
        key: redis key
        value: str, dict, list
        ex: expire time in seconds
        px: expire time in milliseconds
        kwargs: 其他 redis set 参数
        """
        # 如果是 dict/list，序列化成 json
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        # str 或其他类型直接存
        await self._r.set(key, value, ex=ex, px=px, **kwargs)

    async def get(self, key: str) -> Union[str, dict, list, None]:
        val = await self._r.get(key)
        if val is None:
            return None
        try:
            # 尝试反序列化 json
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            # 不是 json 就直接返回字符串
            return val

    async def expire(self, key: str, expire: int):
        """ 为已存在的 key 设置过期时间"""
        await self._r.expire(name=key, time=expire)

    async def ttl(self, key: str) -> int:
        """检查剩余时间"""
        return await self._r.ttl(name=key)

    async def scan_keys_by_prefix(self, prefix: str):
        cursor = 0
        keys = []
        pattern = f"{prefix}*"

        while True:
            cursor, batch = await self._r.scan(cursor=cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        return keys

    async def delete(self, key: str):
        await self._r.delete(key)

    async def close(self):
        await self._r.close()
        await self._r.connection_pool.disconnect()

    async def lpush(self, key: str, value: Any) -> bool:
        """
        将元素插入到 Redis 列表的头部
        key: redis key
        value: str, dict, list
        """
        # 如果是 dict/list，序列化成 json
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        # 将元素推入列表头部
        await self._r.lpush(key, value)
        return True

    async def rpop(self, key: str) -> Union[str, dict, list, None]:
        """
        从 Redis 列表的尾部取出元素
        key: redis key

        返回值：返回列表中的一个元素，可能是 JSON 格式或者普通字符串
        """
        val = await self._r.rpop(key)
        if val is None:
            return None
        try:
            # 尝试反序列化 json
            return json.loads(val)
        except json.JSONDecodeError:
            # 不是 json 格式就直接返回字符串
            return val.decode("utf-8") if isinstance(val, bytes) else val  # 将字节串解码为字符串

    @staticmethod
    def iso_to_standard_datetimestr(datestr: str, time_zone_step: int) -> str:
        """iso(2024-04-21T04:20:00Z)格式转 标准的时间格式(2024-01-01 00:00:00)"""
        dt_str = "{} {}".format(datestr[:10], datestr[11:-1])
        dt = datetime.strptime(dt_str, standard_date_format)
        dt_step = dt + timedelta(hours=time_zone_step)
        return dt_step.strftime(standard_date_format)

    def iso_to_standard_datestr(self, datestr: str, time_zone_step: int) -> str:
        """iso(2024-04-21T04:20:00Z)格式转 标准的时间格式(2024-01-01)"""
        return self.iso_to_standard_datetimestr(datestr=datestr, time_zone_step=time_zone_step)[:10]

    @staticmethod
    def general_key_vid(last_time_ticket: str) -> int:
        last_time = datetime.strptime(last_time_ticket, '%Y-%m-%d %H:%M:%S')
        delta = last_time - datetime.now()
        seconds = delta.total_seconds()
        if seconds >= 0:
            return int(seconds)
        else:
            return 86400

    async def is_exists_in_set(
            self, key: str, value: str
    ) -> Union[Awaitable[Union[Literal[0], Literal[1]]], Union[Literal[0], Literal[1]]]:
        """
        判断元素是否在集合中
        """
        return await self._r.sismember(key, value)

    async def add_to_set(self, key: str, value: str) -> bool:
        """
        添加元素到集合中
        :param key: redis key
        :param value: 存储的内容
        :return:
            True  -> 原来不存在，已成功添加
            False -> 已存在
        """
        result = await self._r.sadd(key, value)
        return result == 1

    async def add_many_to_set(self, key: str, values: Iterable[str]) -> int:
        """
        批量添加元素到集合中
        :param key: redis key
        :param values: 批量存储的内容
        :return: 实际新增的数量
        """
        return await self._r.sadd(key, *values)

    async def remove_from_set(self, key: str, value: str) -> bool:
        """
        从集合中删除元素
        :param key: redis key
        :param value: 要删除的内容
        """
        result = await self._r.srem(key, value)
        return result == 1

    async def members_from_set(self, key: str) -> List[str]:
        """
        获取集合所有成员
        """
        return list(await self._r.smembers(key))

    async def size_set(self, key: str) -> int:
        """
        获取集合大小
        """
        return await self._r.scard(key)

    async def clear_set(self, key: str):
        """
        删除整个集合
        """
        await self._r.delete(key)


class AsyncReliableQueue:
    """
    循环可靠队列（适合 Cron/定时任务）
    """

    def __init__(self, redis: redis.Redis, key: str):
        self.redis = redis
        self.pending = ":".join(["queue", "pending", key])
        self.processing = ":".join(["queue", "processing", key])

        # 使用 Lua 做 pop（原子操作）
        self.pop_script = redis.register_script("""
        -- 从队尾取出
        local task = redis.call('RPOP', KEYS[1])
        if not task then
            return nil
        end
        -- 放入 processing
        redis.call('LPUSH', KEYS[2], task)
        return task
        """)

    async def lpush_if_not_exists(self, task: str):
        CHECK_AND_PUSH = """
        local exist = redis.call('LPOS', KEYS[1], ARGV[1])
        if not exist then
            return redis.call('LPUSH', KEYS[1], ARGV[1])
        else
            return 0
        end
        """
        return await self.redis.eval(CHECK_AND_PUSH, 1, self.pending, task)

    async def add(self, task: str) -> None:
        """生产者：插入队首（FIFO 原生支持）"""
        await self.redis.lpush(self.pending, task)

    async def pop(self) -> Optional[str]:
        """消费者：FIFO 从队尾取出任务，并放入 processing（原子操作）"""
        return await self.pop_script(keys=[self.pending, self.processing], args=[])

    async def finish(self, task: str):
        """任务完成：从 processing 中删除"""
        await self.redis.lrem(self.processing, 1, task)

    async def requeue(self, task: str):
        """任务回队首：从 processing 删除 → 回 pending 队首"""
        pipe = self.redis.pipeline()
        await pipe.lrem(self.processing, 1, task)
        await pipe.lpush(self.pending, task)
        await pipe.execute()

    async def recover(self):
        """恢复崩溃中的任务：processing → pending 队首"""
        tasks = await self.redis.lrange(self.processing, 0, -1)
        if not tasks:
            return 0

        pipe = self.redis.pipeline()
        for t in tasks:
            await pipe.lrem(self.processing, 1, t)
            await pipe.lpush(self.pending, t)
        await pipe.execute()

        return len(tasks)
