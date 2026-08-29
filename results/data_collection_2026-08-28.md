# 2026-08-28 五路同步直接抓角数据记录

## 结论先行

今天已完成 100 条正式直接抓角示教的采集，并开始从同一批五路同步源数据派生三个单外部视角 LeRobot 数据集。检查时转换进程仍在运行，因此本记录只证明“已采集、正在转换”，不证明三份训练集已经完整或可开始训练。

## 原始数据口径

- 任务：`pick_corner`；每条示教为接近指定材料角、闭合、抬升并稳定保持。
- 五路同步视觉：Orbbec、D435i1、D435i2、左腕、右腕。
- 操作者报告：今天完成 100 条正式数据。
- 只读检查发现 `/home/alpha/physical_ai_runtime/data/episodes/pick_corner` 下有 `episode_000000`–`episode_000100`，共 101 个成功目录；另有 4 个失败目录。
- 这 101 个成功目录均不能自动等同于 101 条正式训练示教。冻结 split 前需确认其中 1 条是否为冒烟或额外样本，并保存最终 100 个 source ID 清单。

## 转换快照

检查时间：2026-08-28 19:34（Asia/Shanghai）。转换命令仍在运行：`--task pick_corner --camera-view paired3 --require-accepted-demonstration`。

当时三个数据集均已完成 74 个 source episodes；转换器正在继续写后续 episode，因此不同文件计数可能短暂不一致。

| 数据集 | 快照 episodes | 快照 frames | 外部视角 | 每条样本的视觉输入 |
|---|---:|---:|---|---|
| `/home/alpha/lerobot_train/pick_corner_orbbec` | 74 | 26,102 | Orbbec | `top + left_wrist + right_wrist` |
| `/home/alpha/lerobot_train/pick_corner_d435i1` | 74 | 26,102 | D435i1 | `top + left_wrist + right_wrist` |
| `/home/alpha/lerobot_train/pick_corner_d435i2` | 74 | 26,102 | D435i2 | `top + left_wrist + right_wrist` |

共同的 74 条 manifest 记录具有以下属性：

- 30 Hz，图像为 640×480 H.264；
- state 和 action 均为 14 维；
- 三份 source ID 顺序一致，frame 总数一致；
- 已转换标签均为 `accepted_success`、`stable_corner_grasp_success=true` 且 `human_verified=true`；
- source index 在 `0–72` 中暂缺 `68/69/70`，但这三条原始记录也标为 accepted-success；转换结束后必须查明是处理中、被跳过还是失败，不能仅按 dataset index 推断 source 完整性。

上述数字是转换中的瞬时快照，最终报告不得直接引用为完成数量。

## 转换完成后的验收门槛

1. 先确定恰好 100 个正式 `source_episode_id`，再冻结 80/10/10 split。
2. 三份数据都必须有 100 个 manifest entries、100 个 parquet、每个相机 key 各 100 个视频。
3. 同一 source 在三份数据中的 fingerprint、frame 数、state、action、timestamp 和腕部画面必须一致。
4. 三份数据只允许外部 `top` 图像来源不同；不能出现 source 顺序错位或跨 split 泄漏。
5. 完成随机视频抽查和实际 dataloader tensor 导出后，才把状态更新为“可训练”。

## 实验含义

三份数据来自同一批动作示教，所以 E1/E2/E3 各有 100 条独立示教；Mix-1 是 100 个 source episodes 展开成 300 个视角条件样本，不是 300 条独立示教。训练比较必须固定 source split 和 optimizer updates，并加入最佳单视角重复采样的 Single-repeat 对照。
