# 实验结果目录

`result_schema.csv` 是逐次试验的最小字段模板。正式结果应一行对应一次 trial，不要只保存汇总成功率。

`baseline_corner_approach_test1_020000.md` 冻结了 2026-08-26 训练的只接近
角点模型及其当前验收门。它是基线登记，不是实机成功结果。

`artifacts/corner_following_analyzer_smoke` 是自动测量工具在既有遥操作 episode 上的
离线链路验证，不是 `M=30` policy 结果。`artifacts/` 已被 Git 忽略；正式摘要应在
人工真机录制完成、核对叠图后另行整理进本目录。

原始视频、机器人日志和包含个人信息或体积较大的数据不应直接提交到公开仓库，除非已经完成脱敏、许可和存储方案确认。
