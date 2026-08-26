# 实验结果目录

`result_schema.csv` 是逐次试验的最小字段模板。正式结果应一行对应一次 trial，不要只保存汇总成功率。

多视角实验应特别注意：

- `external_camera_count` 只统计外部观察相机，腕部相机单独记录；
- `source_episode_id` 保留同步视角共同来源，避免把同一示教重复计数；
- `*_visibility` 使用 `visible / partial / occluded / unknown`；
- `camera_intervention` 记录 mask、错帧替换或局部遮挡；
- `correspondence_*` 字段只有在运行对应评估时填写，否则留空；
- 自动标签必须保留 `label_source` 和人工复核状态。

原始视频、机器人日志和包含个人信息或体积较大的数据不应直接提交到公开仓库，除非已经完成脱敏、许可和存储方案确认。
