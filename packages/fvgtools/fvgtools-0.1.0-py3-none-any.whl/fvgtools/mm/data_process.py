import random
from fvgtools.utils import load_jsonl_as_list

__all__ = ['sample_jsonl_by_repeat_time']

def sample_jsonl_by_repeat_time(jsonl_path, repeat_time, random_seed=None):
    """
    根据repeat_time对JSONL文件进行采样或重复。
    
    参数:
        jsonl_path (str): JSONL文件路径，可以是本地路径或S3路径（以's3://'开头）
        repeat_time (float): 采样/重复参数：
            - 如果 0 < repeat_time <= 1.0：表示采样比例（例如0.5表示保留50%的数据）
            - 如果 repeat_time > 1.0：表示每个样本重复的次数（例如2.0表示每个样本重复2次，
                                      2.5表示每个样本重复2次，并有50%概率再重复1次）
        client (optional): S3客户端实例，当读取S3路径时必需
        random_seed (int, optional): 随机种子，用于可重复的采样结果
        
    返回:
        list: 处理后的数据列表，每个元素是一个dict
        
    异常:
        ValueError: 如果repeat_time <= 0
        
    示例:
        >>> # 每个样本重复2.3次（平均）
        >>> repeated_data = sample_jsonl_by_repeat_time('data.jsonl', 2.3)
        
        >>> # 使用随机种子保证可重复性
        >>> sampled_data = sample_jsonl_by_repeat_time(
        ...     'data.jsonl', 0.5, random_seed=42
        ... )
    """
    if repeat_time <= 0:
        raise ValueError(f"repeat_time必须大于0，当前值: {repeat_time}")
    
    # 设置随机种子（如果提供）
    if random_seed is not None:
        random.seed(random_seed)
    
    # 加载原始数据
    data = load_jsonl_as_list(jsonl_path)
    
    # 分解repeat_time为整数部分和小数部分
    int_part = int(repeat_time)
    frac_part = repeat_time - int_part
    
    result = []
    
    # 处理整数部分：每个样本重复int_part次
    if int_part > 0:
        result.extend(data * int_part)
    
    # 处理小数部分：随机采样frac_part比例的数据
    if frac_part > 0:
        sample_size = int(len(data) * frac_part)
        result.extend(random.sample(data, sample_size))
    
    return result