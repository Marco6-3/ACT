# 下一步实验（2026-09-01 冻结版）

当前已完成 E1/E2/E3 三个原生单视角模型的 `M=10/20/30` 初筛、E3-Orbbec
跨相机零样本测试，以及旧 E4/Mix-1-300 三视角探索评估。旧 E4 在 D435i1、D435i2、
Orbbec 上分别为 `1/10`、`0/10`、`0/9`，但它使用 300 个 dataset episodes，而单视角
基线各为 100，不能作为严格等样本量结论。现已用 seed 1000 将 100 个唯一 source
episodes 互斥分配为 D435i1/D435i2/Orbbec=`33/33/34`，重建受控 Mix-1-100。
下一阶段冻结三组新实验：`Mix-1-100@20k`、`Mix-1-300@60k` 和 `All-3@20k`。
旧 checkpoint `outputs/pick_corner4` 只保留为 20k pilot，不并入这三组新结果。

## 已完成结果

人工判定 `T/F` 以操作员记录为准；成功定义为左右夹爪抓住两个指定角、抬升 10 cm
并保持 3 s。括号内为二项比例的 95% Wilson 区间。

| 原生单视角模型 | M=10 | M=20 | M=30 |
|---|---:|---:|---:|
| E1-D435i1 | 0/10，0%（0–27.8%） | 3/10，30%（10.8–60.3%） | 5/10，50%（23.7–76.3%） |
| E2-D435i2 | 0/10，0%（0–27.8%） | 6/10，60%（31.3–83.2%） | 3/10，30%（10.8–60.3%） |
| E3-Orbbec | 1/10，10%（1.8–40.4%） | 8/10，80%（49.0–94.3%） | 4/10，40%（16.8–68.7%） |

跨相机 OOD 初筛固定 E3 checkpoint 和 `M=20`：换 D435i1 为 0/5，换 D435i2
为 0/5。该结果表示当前 E3 模型在这两个未训练相机上没有观察到零样本迁移，不推广
为“所有单视角训练都不具备跨视角迁移能力”。0/5 的 95% Wilson 区间上界仍为 43.4%。

数据台账有两个已知限制：E1-D435i1 M=10 因确定连续失败只保存了 6 条 episode，
人工统计仍记为 0/10，但未保存的 4 条不能用于遥测或失败机制分析；E3-Orbbec M=10
目录有 12 条 episode，本表按操作员确认的正式 10 条结果记为 1/10，不从目录数量反推
成功率。后续所有失败和超时都必须保存，避免再次出现结果与 episode 无法逐条对应。

旧 E4/Mix-1-300 固定 `M=20`：D435i1 为 1/10（10%），D435i2 为 0/10（0%），Orbbec
为 0/9（0%）。Orbbec 少 1 次，因此三组并非完全平衡的正式比较；但三个方向都未优于
对应原生基线。由于训练集 episode 数为基线的三倍，这只能作为旧配置负向 pilot，不能
替代新 Mix-1-100 的等样本量复验，也不否定同一时刻输入三台外部相机的 All-3 融合。

## 当前解释与参数冻结

- 分层结果中有两个视角在 `M=20` 达到各自最高值；三视角描述性合计为 17/30，
  高于 `M=30` 的 12/30 和 `M=10` 的 1/30。因此后续 E1–E4 研究比较暂定冻结
  `M=20`。
- 这不证明 `M=20` 是 ACT、任意相机或未来所有部署的通用最优值。每组只有 10 次，
  区间很宽，而且 D435i1 的观察最优值是 `M=30`。
- 研究比较阶段不能为 D435i1 单独改用 `M=30`，否则模型差异与 M 差异混杂。若以后
  确定只部署 E1-D435i1，可另做配对复验后在该部署配置中选择 `M=30`。

## 所有后续探索 trial 的共同规则

- 成功、超时和无效 trial 的判定保持不变；抓错角、只抓住一侧和 60 s 超时均为失败；
- 布局：`L1=C`，`L2/L3=图像左/右 30 mm`，`L4/L5=图像上/下 30 mm`；
- 当前每个 10-trial 条件中每个布局出现 2 次，使用与已有 M=20 基线一致的顺序：
  `L5,L4,L3,L2,L1,L1,L2,L3,L4,L5`；
- 毛巾朝向和平整度不变，固定顶灯/窗帘，并记录明显阴影、反光或自动曝光异常；
- 推理统一使用“后台推理、等待期不重发 hold”的当前 runtime；正式运行中
  `hold_action_count` 必须为 0；
- 失败和超时也按 `S` 保存。只有摆放错误、人工碰撞、急停或录制损坏等无效 trial
  才按 `D` 删除并重测；
- 从本阶段开始建立逐 trial 台账，至少记录 `task/episode_index/layout/T-F/failure_code`，
  使人工结果能够和 episode 唯一对应。

## 接下来的门控顺序

| Gate | 条件 | 训练预算 / 测试次数 | 回答的问题 |
|---|---|---:|---|
| 0（已完成） | E4/Mix-1 checkpoint GPU dry-run | 1 次 | 操作员报告通过；未保存日志，不作为正式证据 |
| 1（已完成） | E4 分别配 D435i1、D435i2、Orbbec | 每视角 1 次真机 smoke | 操作员报告安全通过；未保存 episode，不计入成功率 |
| 2（旧 pilot 已完成） | E4/Mix-1-300@20k 分别配三个顶部视角，M=20 | 10、10、9 次 | 三个方向均退化，但训练预算口径不匹配且测试不平衡 |
| 3（已完成） | 重建互斥分层抽样的 Mix-1-100 | 33/33/34，共 100 | 已验收 100 episodes、100 个唯一 source |
| 4（已完成） | 保留完整 Mix-1-300 与转换 E6/All-3 | 300 / 100 episodes | 两份训练输入均来自相同 100 个 source episodes |
| 5 | Mix-1-100：每条只输入一个顶部视角 | 20,000 steps；三个顶部视角各 10 次 | 固定样本数和 updates 时，视角混训是否优于专用单视角 |
| 6 | Mix-1-300：每个 source 展开三个单顶部视角样本 | 60,000 steps；三个顶部视角各 10 次 | 按 3 倍样本量同步增加到 3 倍 updates 后，完整视角覆盖是否有帮助 |
| 7 | E6/All-3：每条同时输入三个顶部视角和两个腕部视角 | 20,000 steps；10 次 | 同时多视角是否提供推理期互补信息 |
| 8（按三组结果触发） | 补样、Single-repeat 或相机 mask/错帧干预 | 另行冻结 | 只追查三组中出现的明确增益 |

当前不补原生 M=20 基线。E1/E2/E3 已有的各 10 次用于和新 Mix-1-100 做第一轮筛查；
两个 Mix-1 模型都必须分别在 D435i1、D435i2 和 Orbbec 上测试，All-3 则固定同时输入
三台顶部相机。每个新条件的 10 次只能做探索门控，不能支持稳定优越性或最终部署
成功率结论。三个训练任务使用相同 seed、动作标签、checkpoint 规则和 source episodes；
`100@20k` 与 `300@60k` 的 optimizer updates / dataset episodes 比值都为 200，且保持
batch size 等其余训练配置一致。

## 进入真正多视角融合的决策规则

两个 Mix-1 条件每条样本都只输入一个外部视角，因此属于多视角数据混训，不是同时
多相机融合。Mix-1-100@20k 是与单视角基线对齐的样本数/updates 控制；
Mix-1-300@60k 保留每个 source 的全部三个视角，并按数据量同比增加训练预算；
All-3@20k 则直接回答“额外相机在推理时同时可见是否提供互补信息”。三者必须使用
新 checkpoint 和独立结果台账，不能复用旧 `pick_corner4` 结果。

All-3 必须创建 5 图像 feature schema、重新训练并使用 runtime 的
`--camera-view all3`，不能由切换 E4 的 `top` topic 代替。首轮不做三个两外部相机组合。
结果按以下规则解释：只有 Mix-1-300@60k 改善时，先用 Single-repeat/训练预算控制
排除更多曝光的解释；只有 All-3 改善时，优先验证推理期遮挡或深度互补；三组均未
超过各自匹配基线且失败类型不变时，停止 Random-2、跨视角 loss 和蒸馏，转向示教、
反馈、接触与控制方法。若任一组明确改善，再补配对样本并做逐相机 mask、错帧和遮挡
干预。

## 多视角收尾后的下一主线：Experiment A → Experiment C

如果 Gate 5–7 均没有形成可靠增益，或者即使有小幅数值改善但主要失败机制仍是“第一侧抓取失败后第二侧继续错误阶段动作”，下一主线冻结为示教时序一致性，而不是继续添加相机或跨视角 loss。

### Experiment A：Mixed-order vs Fixed-order

使用已有 Orbbec + wrists 数据，不先采新数据。按首次闭合侧构建：

| 条件 | 数据 | 训练预算 |
|---|---:|---:|
| A0 Mixed-40 | 20 L-first + 20 R-first | 8k steps |
| A1 Left-first-40 | 40 L-first | 8k steps |
| A2 Right-first-40 | 40 R-first | 8k steps |

40@8k 与当前 100@20k 保持相同 updates/episode 比例。三组固定 batch size、seed 1000、M=20、Orbbec、五布局和 no-hold runtime。每组先 10 trials；若固定顺序相对 Mixed 至少出现 3/10 的绝对成功数优势，或闭合误差/第二侧条件成功率有清晰改善，再扩到至少 20 trials 并补训练 seed。

如果 Fixed-order 与 Mixed-order 基本一致，则停止时序多模态主线，不实现 Phase-ACT。

### Experiment C：Phase-ACT

只有 Experiment A 支持时序一致性效应后启动。先在 mixed-order 数据上比较：

1. `C0 Raw-ACT`；
2. `C1 Oracle-Phase ACT`：真实 phase token，验证 phase 信息上限；
3. `C2 Predicted-Phase ACT`：phase classifier + phase embedding + ACT，可部署方案。

首版 phase：`P0 approach / P1-L / P1-R / P2 second-side align / P3 dual-grasp / P4 lift-hold`。没有 corrective demonstrations 之前不加入 recovery phase。

只有 C1 明显优于 C0 才继续 C2；如果 C1 都无收益，立即停止 Phase-ACT。完整协议、机制指标和 kill criteria 见 [`TEMPORAL_CONSISTENCY_PHASE_ACT_PLAN.md`](./TEMPORAL_CONSISTENCY_PHASE_ACT_PLAN.md)。

已完成门槛的复现命令和 E4 十次探索命令见
`/home/alpha/physical_ai_runtime/apps/README.md` 第 7 节。
