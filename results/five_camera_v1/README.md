# Five-camera v1 results

本目录保留五相机链路预检证据和未来 E1–E4 评估汇总。正式原始任务现为
`physical_ai_runtime/data/episodes/pick_corner`；三个 LeRobot 数据集位于
`/home/alpha/lerobot_train/pick_corner_orbbec`、`pick_corner_d435i1` 和
`pick_corner_d435i2`。ACT 只登记研究证据和结果，不保存或生成运行命令。

- `collection_readiness/`：时钟、五路频率/分辨率、首帧拼图与短 MCAP 检查。
- `../data_collection_2026-08-28.md`：采集与转换中的数据快照。
- `../data_acceptance_2026-08-29.md`：100 条有效数据的全量验收与 3 条损坏 source 的隔离依据。
- `../e1_e3_grasp_failure_diagnosis_2026-08-29.md`：E1–E3 checkpoint、示教闭合时序、离线误差与真机失败诊断。
- `data_acceptance_2026-08-29.json`：100 条 source、900 个视频的机器可读验收结果。
- `data_acceptance_contact_sheet_2026-08-29.jpg`：source `0/49/100` 的三视角视觉抽检。
- `new_sources_101_102_contact_sheet_2026-08-29.jpg`：两条补采 source 的三视角视觉抽检。
- `source_split.json`：已冻结的 100 条 source episode 80/10/10 划分。
- `summary.csv`：逐 trial 主表。
- `corner_error/`、`grasp_success/`、`failure_modes/`：图和派生统计。
- `report.md`：最终结论与 Go/No-Go。

禁止手工把同一 source episode 的不同视角放入不同 split。
