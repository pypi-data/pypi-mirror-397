from numba import cuda
import numpy as np

# -----------------------------------------------
# 1. 这是一个 CUDA Kernel (内核)
# 它不是在 CPU 跑，而是在 GPU 的每个线程上跑
# -----------------------------------------------
@cuda.jit
def _vector_add_kernel(a, b, result):
    # 计算当前线程在整个网格中的绝对 ID
    # 相当于：我是第几个干活的“小人”
    idx = cuda.grid(1)
    
    # 边界检查：防止线程数多于数组长度时越界
    if idx < result.size:
        result[idx] = a[idx] + b[idx]

# -----------------------------------------------
# 2. 这是一个 Python 包装函数 (Host 端)
# 负责内存分配、数据拷贝、启动内核
# -----------------------------------------------
def vector_add_gpu(a_list, b_list):
    """
    使用 GPU 计算两个列表/数组的和
    """
    # 强制转换为 numpy 数组，类型为 float32 (GPU 常用类型)
    a = np.array(a_list, dtype=np.float32)
    b = np.array(b_list, dtype=np.float32)
    n = a.size

    # --- 显存管理 (Memory Management) ---
    # 把数据从 CPU 内存 拷贝到 GPU 显存
    d_a = cuda.to_device(a)
    d_b = cuda.to_device(b)
    # 在 GPU 上申请一块空间放结果
    d_result = cuda.device_array_like(a)

    # --- 配置线程块 (Block) 和 网格 (Grid) ---
    threads_per_block = 256
    # 向上取整，确保有足够的线程覆盖所有数据
    blocks_per_grid = (n + (threads_per_block - 1)) // threads_per_block

    # --- 启动内核 (Launch Kernel) ---
    # 语法: kernel_name[blocks, threads](arguments)
    _vector_add_kernel[blocks_per_grid, threads_per_block](d_a, d_b, d_result)
    
    # --- 等待 GPU 跑完并把结果拷回 CPU ---
    # copy_to_host() 会自动同步
    return d_result.copy_to_host()