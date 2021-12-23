from functools import wraps
import time


def performance(func):
    @wraps(func)
    def with_performance(*args, **kwargs):
        start_time = time.time()
        # 関数を実行
        res = func(*args, **kwargs)
        # 実行時間を計算して、プリントする
        run_time = time.time() - start_time
        print("%s was called in: %fs" % (func.__name__, run_time))
        return res

    return with_performance
