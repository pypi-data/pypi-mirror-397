import time
import math
import random


def get_auto_task_limit(running: float, reference_speed: int, wave: int, *args, **kwargs):
    """自动并发策略"""
    percent = reference_speed / wave
    return int(
        reference_speed + percent * math.cos(math.pi * running / 2)
    )


def get_random_task_limit(min_speed: int, max_speed: int):
    """随机并发策略"""
    return random.randint(min_speed, max_speed)


def get_speed_task_limit(task_limit: int, avg_speed: int, current_speed: int):
    """速度并发策略，根据设定并发速度系统自动调整"""

    if task_limit >= current_speed * 2:
        return task_limit

    new_limit = int(current_speed * avg_speed / task_limit)

    return new_limit if new_limit else 1


def get_time_task_limit(min_limit: int, max_limit, current_speed, running: float, second: int, waiting_count: int):
    """时间并发策略，根据设定并发时间系统自动完成爬取任务"""

    logical_remaining = second - running

    if waiting_count == 0 or logical_remaining <= 0:
        return min_limit

    new_limit = int(waiting_count / logical_remaining)

    if new_limit <= 0:
        return min_limit
    elif new_limit >= current_speed * 2:
        return max_limit
    else:
        return new_limit


def get_task_limit(config, crawling_time, current_speed, task_limit, waiting_count):

    if config.auto['enabled']:
        running = round(time.time() - crawling_time, 3)
        return get_auto_task_limit(running, config.auto['reference_limit'], config.auto['wave'])
    elif config.fix['enabled']:
        return config.fix['task_limit']
    elif config.random['enabled']:
        return get_random_task_limit(config.random['min_limit'], config.random['max_limit'])
    elif config.speed['enabled']:
        return get_speed_task_limit(task_limit, config.speed['avg_speed'], current_speed)
    elif config.time['enabled']:
        running = round(time.time() - crawling_time, 3)
        return get_time_task_limit(
            config.time['min_limit'], config.time['max_limit'], current_speed, running,
            config.time['second'], waiting_count
        )
    else:
        raise
