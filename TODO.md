# TODO — ACT 多视角角点抓取实验

> 状态更新（2026-08-28）：今天已完成 100 条正式五路同步直接抓角示教。原始成功目录当前为
> `episode_000000`–`episode_000100`（共 101 条），因此冻结数据集前必须确认其中哪 1 条是冒烟或额外样本，不能直接把 101 条都计入“100 条正式示教”。三份 LeRobot 单外部视角数据正在转换，尚未通过最终验收。

> 项目边界：ACT 只保存研究问题、实验规划、数据快照、训练/评估设计和结果；相机/机器人启动、采集、转换、训练与控制程序归 `/home/alpha/physical_ai_runtime`。本仓库不再维护这些运行代码的副本。

完整研究路线见 [`docs/MULTIVIEW_RESEARCH_PLAN.md`](./docs/MULTIVIEW_RESEARCH_PLAN.md)，今日可复核快照见 [`results/data_collection_2026-08-28.md`](./results/data_collection_2026-08-28.md)。

## P0：冻结今日数据（转换完成后立即执行）

- [x] 采集 100 条正式直接抓角示教，每条同步记录 3 个外部相机和 2 个腕部相机
- [x] 每条已转换记录带有人工确认的 `accepted_success` 与 `stable_corner_grasp_success=true`
- [ ] 识别并排除 101 个成功目录中的 1 条冒烟/额外 episode，冻结恰好 100 个 `source_episode_id`
- [ ] 等待 `pick_corner_orbbec`、`pick_corner_d435i1`、`pick_corner_d435i2` 全部转换结束；转换运行中不做最终统计
- [ ] 验收三份数据均为 100 episodes，且 `total_episodes`、manifest 长度、parquet 数及每路视频数一致
- [ ] 逐 source episode 核对三份数据的 `source_episode_id`、fingerprint、frame 数、state、action 与 timestamp 完全配对
- [ ] 核对统一模型输入为 `observation.images.top + left_wrist + right_wrist`，仅 `top` 的外部相机来源不同
- [ ] 抽查三视角及腕部视频，排除错相机、黑帧、裁剪、翻转和 RGB/BGR 问题
- [ ] 按 `source_episode_id` 一次性冻结 80/10/10 train/validation/test；禁止按帧切分或让同步视角跨 split

停止标准：任一视角缺 episode、帧数不配对、fingerprint 不一致、视频损坏或存在 split 泄漏时，不开始训练。

## P0：第一阶段训练矩阵

| 条件 | 每条样本输入 | 独立 source episodes | 视角条件样本 | 目的 |
|---|---|---:|---:|---|
| E1-Orbbec | `orbbec + wrists` | 100 | 100 | 单视角基线 |
| E2-D435i1 | `d435i1 + wrists` | 100 | 100 | 单视角基线 |
| E3-D435i2 | `d435i2 + wrists` | 100 | 100 | 单视角基线 |
| E4/Mix-1 | 每条取一个外部视角 `+ wrists` | 100 | 300 | 检验视角混合 |
| Single-repeat | 最佳单视角重复采样 | 100 | 300 | 排除更多 updates/重复曝光的混杂 |

- [ ] E1/E2/E3 使用同一 source split、动作标签、训练预算、种子和 checkpoint 规则
- [ ] E4 只在各 split 内展开三视角，并平衡采样 `orbbec/d435i1/d435i2`
- [ ] 固定 optimizer updates；同时训练 Single-repeat，不能把 E4 的三倍曝光误归因为视角收益
- [ ] 保存每次运行的数据 manifest、代码提交、超参数、随机种子、checkpoint 与训练曲线
- [ ] 训练完成后先做离线输入/动作 sanity check，再进入真机评估

## P0：配对真机筛查

- [ ] 预先冻结毛巾方向、位置、褶皱和目标角的布局编号
- [ ] 每个主要条件至少 20 次，使用相同布局并随机化方法执行顺序
- [ ] 主要终点：双侧指定材料角抬升 10 cm 并保持 3 s 的成功率及 95% 置信区间
- [ ] 机制指标：左右闭合误差、双角进入物理捕获区域比例、左右/双角夹持率和抬升保持率
- [ ] 人工复核成功标签与失败类型；自动标签不直接作为最终真值
- [ ] 分别报告 E4 在三个部署外部视角上的性能，不只报告合并平均值

## Go/No-Go

- [ ] E4 同时优于最佳单视角与 Single-repeat，并在多个测试视角下达到预设最小有意义差异：进入 Random-2 / All-3
- [ ] E4 无可靠提升：暂停多视角扩展，回查反馈带宽、动作执行和接触瓶颈
- [ ] E4 只在一个视角提升：先检查采样平衡、相机方位偏差和可见性，不声称跨视角表征成立
- [ ] 只有同时多视角收益与闭合误差/不确定度下降一致时，才进入跨视角材料点一致性与单视角蒸馏

## 仍需补齐的基础测量

- [ ] 测量真实夹爪捕获区域 `C(e_x,e_y,e_z,e_yaw)`，替代“角点附近 1–2 cm”的主观阈值
- [ ] 记录 prediction horizon `K`、executed steps per query `M`、query/control frequency、temporal ensemble 和端到端延迟
- [ ] 在 50/30/15 mm 阶段做 late-perturbation 配对实验，测响应延迟和误差收缩率 `rho`

## 历史记录（不再作为当前门槛）

- 2026-08-26 的 40 条 approach-only 模型 `test1/020000` 仅证明旧 pipeline 能产生粗粒度跟随现象；不代表直接抓角成功。
- 旧的采集启动、ROS 预检、转换器和控制侧待办已移出 ACT；对应实现与运行证据应在 Physical AI Runtime 维护。
