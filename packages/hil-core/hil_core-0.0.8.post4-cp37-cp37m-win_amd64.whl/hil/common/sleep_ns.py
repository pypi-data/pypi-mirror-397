import time
import ctypes
import sys
import ctypes
import ctypes.util
import time


__author__ = 'notmmao'
__email__ = 'notmmao@gmail.com'


def precise_sleep(duration_sec):
    """
    跨平台高精度睡眠函数
    :param duration_sec: 睡眠时间，单位秒 (可以是浮点数)
    """
    if sys.platform == 'win32':
        _precise_sleep_windows(duration_sec)
    else:
        _precise_sleep_linux(duration_sec)

def _precise_sleep_windows(duration_sec):
    """Windows 下的高精度睡眠实现"""
    kernel32 = ctypes.windll.kernel32
    
    # 创建可等待计时器
    timer = kernel32.CreateWaitableTimerExW(
        None, None, 0x00000002, 0x1F0003
    )
    
    # 时间单位是 100 纳秒，负值表示相对时间
    delay = ctypes.c_longlong(int(-duration_sec * 10000000))
    
    # 设置计时器
    kernel32.SetWaitableTimer(
        timer, ctypes.byref(delay), 0, None, None, False
    )
    
    # 等待计时器触发
    kernel32.WaitForSingleObject(timer, 0xFFFFFFFF)
    
    # 关闭句柄
    kernel32.CloseHandle(timer)

def _precise_sleep_linux(duration_sec):
    """Linux 下的高精度睡眠实现"""
    try:
        # 尝试使用 clock_nanosleep (最精确)
        librt = ctypes.CDLL(ctypes.util.find_library("rt"), use_errno=True)
        
        class timespec(ctypes.Structure):
            _fields_ = [("tv_sec", ctypes.c_long),
                        ("tv_nsec", ctypes.c_long)]
        
        req = timespec()
        req.tv_sec = int(duration_sec)
        req.tv_nsec = int((duration_sec - req.tv_sec) * 1e9)
        
        CLOCK_MONOTONIC = 1
        result = librt.clock_nanosleep(
            CLOCK_MONOTONIC, 0, ctypes.byref(req), None
        )
        
        if result != 0:
            errno = ctypes.get_errno()
            raise OSError(errno, f"clock_nanosleep failed with errno {errno}")
    
    except Exception as e:
        # 如果 clock_nanosleep 失败，回退到 select
        if duration_sec > 0:
            time.sleep(duration_sec)

