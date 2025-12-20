# -*- coding: utf-8 -*-
"""
本模块功能：宏观经济基本面分析，基于国际货币基金会IMF经济指标。
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年12月9日
最新修订日期：2025年12月10日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
"""
访问IMF数据库的插件：尚未测试
weo-reader
export_ease
imfFetcher
world-economic-outlook
imf-reader
imfp
imfdatapy
https://imfdatapy.readthedocs.io/en/latest/readme.html
"""
#==============================================================================

import requests
import pandas as pd
import urllib3

urllib3.disable_warnings()


def imf(dataset, indicator, country="CN", start="1980", end="2030"):
    """
    最稳定版 IMF 数据获取（WEO/IFS 均可）
    dataset: "WEO" 或 "IFS"
    indicator: 例如 "NGDP_RPCH"
    country: CN/US/JP
    """

    base = "https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData"
    url = f"{base}/{dataset}/{country}.{indicator}?startPeriod={start}&endPeriod={end}"

    # 因 IMF 网络极不稳定，强制重试 8 次
    last_err = None
    for _ in range(8):
        try:
            r = requests.get(url, timeout=20, verify=False)
            if r.status_code == 200:
                data = r.json()
                break
        except Exception as e:
            last_err = e
            continue
    else:
        raise RuntimeError(f"IMF API failed: {last_err}")

    try:
        series = data["CompactData"]["DataSet"]["Series"]
        obs = series["Obs"]
    except Exception:
        return pd.DataFrame(columns=["date", "value"])

    rows = []
    for o in obs:
        t = o.get("@TIME_PERIOD")
        v = o.get("@OBS_VALUE")
        if v not in (None, ""):
            rows.append([t, float(v)])

    df = pd.DataFrame(rows, columns=["date", "value"])
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


if __name__=='__main__':
    df = imf("WEO", "NGDP_RPCH", "CN")
    print(df)
    
    df = imf("IFS", "PCPI_IX", "US")

    df = imf("WEO", "BCA_NGDPD", "JP")

