"""
股票数据增加当天日期，用于记录
"""

import pandas as pd
from datetime import datetime
import akshare as ak

def fetch_data(symbol):
        try:
            df = ak.stock_rank_xstp_ths(symbol=symbol)
            if df is not None and not df.empty:
                df['symbol'] = symbol
                return df
        except Exception as e:
            print(f"{symbol} 失败: {e}")
        return None

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
    
    df['symbol'] = "5日均线"
    symbol_list = ["10日均线", "20日均线", "30日均线", "60日均线", "90日均线", "250日均线", "500日均线"]
    # 过滤掉None值后合并
    df_list = [df for df in (fetch_data(s) for s in symbol_list) if df is not None]
    combined_df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
    total_df = pd.concat([df, combined_df], ignore_index=True)
    total_df['日期'] = datetime.now().strftime("%Y-%m-%d") # 添加日期
    return total_df
