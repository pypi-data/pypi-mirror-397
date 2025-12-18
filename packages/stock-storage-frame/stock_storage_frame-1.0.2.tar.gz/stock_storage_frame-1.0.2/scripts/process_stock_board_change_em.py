# coding: utf-8
"""
板块异动特殊处理
"""

import pandas as pd
from datetime import datetime
import json

# 定义映射字典
t_to_name = {
    1: "顶级买单", 2: "顶级卖单", 4: "封涨停板", 8: "封跌停板",
    16: "打开涨停板", 32: "打开跌停板", 64: "有大买盘", 128: "有大卖盘",
    256: "机构买单", 512: "机构卖单", 8193: "大笔买入", 8194: "大笔卖出",
    8195: "拖拉机买", 8196: "拖拉机卖", 8201: "火箭发射", 8202: "快速反弹",
    8203: "高台跳水", 8204: "加速下跌", 8205: "买入撤单", 8206: "卖出撤单",
    8207: "竞价上涨", 8208: "竞价下跌", 8209: "高开5日线", 8210: "低开5日线",
    8211: "向上缺口", 8212: "向下缺口", 8213: "60日新高", 8214: "60日新低",
    8215: "60日大幅上涨", 8216: "60日大幅下跌"
}

# 定义转换函数
def convert_to_target_format(nested_dict_list):
    try:
        result = {}
        for item in nested_dict_list:
            t = item["t"]
            name = t_to_name.get(t, "未知类型")
            count = item["ct"]
            result[name] = count
        return result
    except Exception as e:
        print(f"处理失败: {e}")
        return {}
    
def process(df: pd.DataFrame) -> pd.DataFrame:
    """
    处理股票数据，计算技术指标。
    
    Args:
        df: 输入的股票数据DataFrame
        
    Returns:
        处理后的DataFrame
    """
    if df.empty:
        return df
    
    df['日期'] = datetime.now().strftime("%Y-%m-%d") # 添加日期
    df["板块具体异动类型列表及出现次数"] = df["板块具体异动类型列表及出现次数"].apply(convert_to_target_format)
    df["板块具体异动类型列表及出现次数"] = df["板块具体异动类型列表及出现次数"].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
    )
    return df
