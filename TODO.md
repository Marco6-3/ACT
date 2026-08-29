# TODO — ACT 多视角角点抓取实验

> 状态更新（2026-08-29）：E1–E4 均已训练至 20,000 steps。用户已定性尝试 E1/E2/E3；共同表现为
> 能到两个角附近，但几乎不能双侧有效抓起。离线诊断发现 100 条示教全部为长间隔串行闭合（中位
> 2.80 s），训练内 TCP 同时刻误差仍为厘米级。本轮选择全部 100 episodes 做全量训练，因此没有执行
> 原先冻结的 80/10/10 科研评估划分；这不代表训练命令无效，也不作为本次抓取失败的直接原因。详见
> [`results/e1_e3_grasp_failure_diagnosis_2026-08-29.md`](./results/e1_e3_grasp_failure_diagnosis_2026-08-29.md)。

> 项目边界：ACT 只保存研究问题、实验规划、数据快照、训练/评估设计和结果；相机/机器人启动、采集、转换、训练与控制程序归 `/home/alpha/physical_ai_runtime`。本仓库不再维护这些运行代码的副本。

完整研究路线见 [`docs/MULTIVIEW_RESEARCH_PLAN.md`](./docs/MULTIVIEW_RESEARCH_PLAN.md)，今日可复核快照见 [`results/data_collection_2026-08-28.md`](./results/data_collection_2026-08-28.md)。

## P0：冻结今日数据（转换完成后立即执行）

- [x] 发现并隔离 3 条损坏 source：`episode_000068`、`episode_000069`、`episode_000070`
- [x] 将 98 条原有效 source 和 2 条补采 source 转换为 `pick_corner_orbbec`、`pick_corner_d435i1`、`pick_corner_d435i2`
- [x] 验收三份 100-episode 数据：各 100 manifest、100 data parquet、100 episode parquet、每路 100 个视频，共 35,474 帧
- [x] 对 100 个 source 核对三份数据的 ID、fingerprint、frame 数、state、action、timestamp 和腕部视频完全配对
- [x] 核对统一模型输入为 `observation.images.top + left_wrist + right_wrist`，仅 `top` 的外部相机来源不同
- [x] 完整解码 900 个视频，并抽查 source `0/49/100/101/102` 三视角画面；未见错相机、黑帧、翻转或 RGB/BGR 问题
- [x] 核对 Orbbec `1280×720 -> 640×480` 为中央裁剪至 `960×720` 后缩放，不是非等比拉伸
- [x] 核对 smoke test 的 150 写入帧转换为 149 帧属于五路共同时间窗边界同步，不是 recorder drop
- [x] 再采集并验收 2 条完整 accepted-success source，使三份数据均达到 100 episodes
- [x] 冻结恰好 100 个 `source_episode_id`：`0–67, 71–102`
- [x] 按 `source_episode_id` 冻结 80/10/10 train/validation/test；三视图共享同一 split

停止标准：任一视角缺 episode、帧数不配对、fingerprint 不一致、视频损坏或存在 split 泄漏时，不开始训练。

## P0：第一阶段训练矩阵

| 条件 | 每条样本输入 | 独立 source episodes | 视角条件样本 | 目的 |
|---|---|---:|---:|---|
| E1-D435i1 | `d435i1 + wrists` | 100 | 100 | 单视角基线；`pick_corner1/020000` |
| E2-D435i2 | `d435i2 + wrists` | 100 | 100 | 单视角基线；`pick_corner2/020000` |
| E3-Orbbec | `orbbec + wrists` | 100 | 100 | 当前部署候选；`pick_corner3/020000` |
| E4/Mix-1 | 每条取一个外部视角 `+ wrists` | 100 | 300 | 检验视角混合 |
| Single-repeat | 最佳单视角重复采样 | 100 | 300 | 排除更多 updates/重复曝光的混杂 |

- [x] E1/E2/E3 使用相同动作标签、20k updates、batch size 4、seed 1000 和 checkpoint 规则完成训练
- [ ] 若要做严格科研对比，重跑 E1/E2/E3 时使用冻结的 80/10/10 source split；本轮是有效的全量 100-episode 训练，`eval_split=0` 表示未在训练中留出验证集
- [x] E4/Mix-1 checkpoint 已完成到 20k；数据按三视角展开，但本轮没有按冻结 split 训练
- [ ] 固定 optimizer updates；同时训练 Single-repeat，不能把 E4 的三倍曝光误归因为视角收益
- [ ] 补齐每次运行的代码提交和训练曲线；当前只有最终 checkpoint 与超参数，没有中间曲线
- [x] E1/E2/E3 完成训练分布内离线 action sanity check；三个模型都能预测闭合，但手臂关节 MAE 约 0.029–0.032 rad
- [ ] 暂停把 E4/Mix-1 当作主要解法；闭合 trace 和短 `M` 配对筛查已完成，尚待推理/控制时序修正与捕获区域测量

## P0：配对真机筛查

- [x] E3 M=30 固定 5 布局完整 trace 已保存：正确双角 2/5、双侧抓错位置 1/5、单侧有效 2/5、抬升滑脱 0/5
- [x] E3 M=10 相同桌面标记配对筛查完成：正确双角 2/5、双侧抓错位置 2/5、单侧有效 1/5、滑脱 0/5；L2 改善，L5 向图像上方偏置重复
- [x] E3 M=5 筛查完成：4/5 达 60 s 超时；L2/L3/L5 trace 中未发出闭合指令，主要受同步推理下动作推进过慢混杂，不解释为抓取落点失败
- [x] 当前部署候选冻结为 E3 M=10；M=5 的实际 query rate 仅约 1.12 Hz，动作推进吞吐约为 M=10 的一半，不再继续缩短 M
- [ ] 核对 M=5/L4 的左右标签：现场称右臂夹住，trace 显示仅 left action/topic 闭合；确认物理臂、操作员视角和 ROS topic 映射
- [x] 30 Hz 重复 hold 已完成真机反证：发布间隔改善，但 L2 从旧 M=10 的成功退化为两次 60 s 未闭合；不得用于正式评估
- [x] 当前候选冻结为后台推理、等待期不重发 joint reference、每 query 仅发布 M=10 新动作；收尾 smoke 中 L1/L3 可成功夹起，最新 L3 trace 双侧闭合且 health PASS
- [ ] L2 持续 timeout；“光照导致策略犹豫”仅为操作员假设。正式测试前冻结顶灯/窗帘状态并记录阴影、反光、自动曝光异常，L2 timeout 仍按失败计数
- [ ] 按 seed `20260829` 的四组分块随机顺序运行 E3-Orbbec M=10 共 20 次；只用 L1–L5 固定 ±30 mm 桌面标记，每布局 4 次
- [ ] E3 正式 20 次完成后，以同一布局、M=10、成功定义和光照协议筛查 E1-D435i1 与 E2-D435i2；checkpoint 与对应 top topic 必须匹配，不能只替换 E3 的相机输入
- [x] 冻结五布局定义：`L1=C`，`L2/L3` 为 Orbbec 图像左/右移 30 mm，`L4/L5` 为图像上/下移 30 mm；保持朝向和平整度不变
- [x] 冻结 20 次正式评估的四组分块随机顺序、逐 trial 登记表和现场执行清单；见 [`docs/E3_M10_FORMAL_EVAL_RUNBOOK.md`](./docs/E3_M10_FORMAL_EVAL_RUNBOOK.md)
- [ ] 开始正式 trial 前，由操作员完成清单中的两项人工门禁：核对物理左右臂/topic 映射；逐视频确认历史 M=10 L1/L2 是否满足 10 cm/3 s（历史结果不计入正式 20 次）

- [ ] 预先冻结毛巾方向、位置、褶皱和目标角的布局编号
- [ ] 每个主要条件至少 20 次，使用相同布局并随机化方法执行顺序
- [ ] 主要终点：双侧指定材料角抬升 10 cm 并保持 3 s 的成功率及 95% 置信区间
- [ ] 机制指标：左右闭合误差、双角进入物理捕获区域比例、左右/双角夹持率和抬升保持率
- [ ] 人工复核成功标签与失败类型；自动标签不直接作为最终真值
- [ ] 正式 trial 增加 lighting note：顶灯/窗帘状态、明显阴影/反光及自动曝光异常；未做控光配对前不声称 L2 因光照失败
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
