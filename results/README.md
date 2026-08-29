# 实验结果目录

`result_schema.csv` 是逐次试验的最小字段模板。正式结果应一行对应一次 trial，不要只保存汇总成功率。

当前数据进度见 [`data_collection_2026-08-28.md`](./data_collection_2026-08-28.md)。该记录区分了“100 条正式数据已采集”“原始成功目录实际为 101 个”和“三份派生数据仍在转换”三种口径；转换完成前不要将中间计数写成最终训练集规模。

多视角实验应特别注意：

- `external_camera_count` 只统计外部观察相机，腕部相机单独记录；
- `source_episode_id` 保留同步视角共同来源，避免把同一示教重复计数；
- `*_visibility` 使用 `visible / partial / occluded / unknown`；
- `camera_intervention` 记录 mask、错帧替换或局部遮挡；
- `correspondence_*` 字段只有在运行对应评估时填写，否则留空；
- 自动标签必须保留 `label_source` 和人工复核状态。
- `stable_corner_grasp_success` 是当前主要任务标签：抓对双侧指定材料角，抬升 10 cm 并保持 3 s，无滑脱且未明显夹入内侧布料；
- `fold_success` 和 `full_task_success` 仅用于未来或附加实验，不能替代当前稳定抓角主要终点。

`baseline_corner_approach_test1_020000.md` 冻结了 2026-08-26 训练的只接近
角点模型。它是已归档的历史 pipeline 诊断，不是实机成功结果，也不再是当前实验门槛。

`artifacts/corner_following_analyzer_smoke` 是自动测量工具在既有遥操作 episode 上的
离线链路验证，不是 `M=30` policy 结果。`artifacts/` 已被 Git 忽略；正式摘要应在
人工真机录制完成、核对叠图后另行整理进本目录。

原始视频、机器人日志和包含个人信息或体积较大的数据不应直接提交到公开仓库，除非已经完成脱敏、许可和存储方案确认。
