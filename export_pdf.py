def gen_pdf(report):
    # 商业版报告生成逻辑
    text = f"""
汽车市场仿真决策报告 (Car-Agent-Simulation)
=========================================
仿真时间：{report.get('time', 'N/A')}
车型：{report.get('model_name', '通用车型')}

1. 必做配置建议：
   {', '.join(report.get('must_have', []))}

2. 高风险舆情雷区：
   {', '.join(report.get('risk', []))}

3. 推荐 KOL 传播类型：
   {', '.join(report.get('kol_best', []))}

4. 竞品动态分析：
   状态：{report.get('competitor_status', '正常')}
=========================================
本报告由 Car-Agent SaaS 引擎自动生成
"""
    return text.encode("utf-8")
