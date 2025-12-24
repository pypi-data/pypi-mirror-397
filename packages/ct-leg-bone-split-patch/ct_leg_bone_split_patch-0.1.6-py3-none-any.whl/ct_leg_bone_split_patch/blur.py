import numpy as np
import cv2
from typing import Optional, Tuple, Union

def gaussian_smooth_2d(
    arr: np.ndarray,
    sigma: Union[float, Tuple[float, float]] = 1.5,
    ksize: Optional[Tuple[int, int]] = None,
    border_mode: int = cv2.BORDER_DEFAULT
) -> np.ndarray:
    """
    对二维NumPy数组进行高斯平滑（高斯模糊），封装OpenCV的GaussianBlur接口，适配多场景
    
    参数说明：
    ----------
    arr : np.ndarray
        输入二维数组（支持uint8/int32/float32/float64类型，如灰度图、数值矩阵）
    sigma : float | Tuple[float, float], 可选
        高斯核标准差：
        - 传单个float：X/Y方向sigma相同（推荐）
        - 传元组(sigmaX, sigmaY)：分别指定X/Y方向的标准差
        默认值：1.5（轻度平滑）
    ksize : Tuple[int, int], 可选
        高斯核尺寸 (宽度, 高度)，必须为奇数（如(5,5)、(7,7)）；
        设为None时，由sigma自动计算最优核尺寸（公式：ksize = 2*int(3*sigma)+1）；
        若手动指定，建议满足 ksize >= 2*int(3*sigma)+1，否则sigma失效
        默认值：None（自动适配）
    border_mode : int, 可选
        边界填充模式，OpenCV常量：
        - cv2.BORDER_DEFAULT（推荐）：反射填充（镜像）
        - cv2.BORDER_CONSTANT：常数填充（需配合borderValue，此处默认0）
        - cv2.BORDER_REPLICATE：复制边缘像素
        默认值：cv2.BORDER_DEFAULT
    
    返回值：
    ----------
    np.ndarray
        平滑后的二维数组，形状、数据类型与输入完全一致
    
    异常抛出：
    ----------
    ValueError: 输入非二维数组、核尺寸非奇数、sigma为负数等非法输入
    TypeError: 输入数组类型不支持
    
    示例：
    ----------
    >>> # 1. 基础用法（默认参数，轻度平滑）
    >>> arr = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
    >>> blurred_arr = gaussian_smooth_2d(arr)
    
    >>> # 2. 自定义sigma和核尺寸（重度平滑）
    >>> blurred_arr = gaussian_smooth_2d(arr, sigma=3.0, ksize=(9,9))
    
    >>> # 3. X/Y方向不同sigma（横向强平滑，纵向弱平滑）
    >>> blurred_arr = gaussian_smooth_2d(arr, sigma=(2.5, 1.0))
    """
    # ====================== 输入参数校验 ======================
    # 1. 检查数组维度
    if arr.ndim != 2:
        raise ValueError(f"输入必须是二维数组，当前维度：{arr.ndim}")
    
    # 2. 检查sigma合法性
    if isinstance(sigma, (int, float)):
        sigmaX = float(sigma)
        sigmaY = float(sigma)
    elif isinstance(sigma, (tuple, list)) and len(sigma) == 2:
        sigmaX, sigmaY = float(sigma[0]), float(sigma[1])
    else:
        raise ValueError(f"sigma必须是数值或长度为2的元组/列表，当前输入：{sigma}")
    
    if sigmaX < 0 or sigmaY < 0:
        raise ValueError(f"sigma不能为负数，当前：sigmaX={sigmaX}, sigmaY={sigmaY}")
    
    # 3. 处理核尺寸（自动计算/校验）
    if ksize is None:
        # 自动计算最优核尺寸（OpenCV默认逻辑）
        def _get_optimal_ksize(s):
            return 2 * int(3 * s + 0.5) + 1 if s > 0 else 1
        ksize_w = _get_optimal_ksize(sigmaX)
        ksize_h = _get_optimal_ksize(sigmaY)
        ksize = (ksize_w, ksize_h)
    else:
        # 手动指定核尺寸：校验是否为奇数
        if len(ksize) != 2:
            raise ValueError(f"ksize必须是长度为2的元组，当前：{ksize}")
        ksize_w, ksize_h = ksize
        if ksize_w % 2 == 0 or ksize_h % 2 == 0:
            raise ValueError(f"ksize必须为奇数，当前：{ksize}")
        if ksize_w < 1 or ksize_h < 1:
            raise ValueError(f"ksize必须大于0，当前：{ksize}")
    
    # 4. 检查数组数据类型（OpenCV支持的类型）
    supported_dtypes = (np.uint8, np.int32, np.float32, np.float64)
    if arr.dtype not in supported_dtypes:
        # 自动转换为兼容类型（如int64→int32，float16→float32）
        if arr.dtype == np.int64:
            arr = arr.astype(np.int32)
        elif arr.dtype == np.float16:
            arr = arr.astype(np.float32)
        else:
            raise TypeError(
                f"不支持的数组类型：{arr.dtype}，支持类型：{[d.__name__ for d in supported_dtypes]}"
            )
    
    # ====================== 执行高斯平滑 ======================
    blurred_arr = cv2.GaussianBlur(
        src=arr,
        ksize=ksize,
        sigmaX=sigmaX,
        sigmaY=sigmaY,
        borderType=border_mode
    )
    
    # ====================== 保证输出类型与输入一致 ======================
    if blurred_arr.dtype != arr.dtype:
        blurred_arr = blurred_arr.astype(arr.dtype)
    
    return blurred_arr