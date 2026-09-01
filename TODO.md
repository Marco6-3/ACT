# TODO — ACT 多视角角点抓取实验

> 状态更新（2026-09-01）：E1/E2/E3 的 `M=10/20/30` 各 10 次初筛、E3 跨相机 OOD
> 初筛和旧 Mix-1-300@20k pilot 已完成。后续统一冻结 `M=20`，执行三组新实验：
> Mix-1-100@20k、Mix-1-300@60k、All-3@20k。三组均无帮助时停止继续扩展多视角，
> 转向其他提高成功率的方法。简明顺序见
> [`docs/NEXT_EXPERIMENTS.md`](./docs/NEXT_EXPERIMENTS.md)。

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
| E1-D435i1 | `d435i1 + wrists` | 100 | 100 | 单视角基线 |
| E2-D435i2 | `d435i2 + wrists` | 100 | 100 | 单视角基线 |
| E3-Orbbec | `orbbec + wrists` | 100 | 100 | 单视角基线 |
| E4a/Mix-1-100@20k | 每条取一个外部视角 `+ wrists`，33/33/34 | 100 | 100 | 等样本/等 updates 检验视角混合 |
| E4b/Mix-1-300@60k | 每个 source 的三个外部视角分别成样本 | 100 | 300 | 完整视角覆盖，保持相同 updates/episode |
| E6/All-3@20k | 三个外部视角同时输入 `+ wrists` | 100 | 100 | 检验推理期多视角互补 |
| Single-repeat@60k | 最佳单视角重复采样 | 100 | 300 | 必要时排除更多 updates/重复曝光的混杂 |

- [x] E1/E2/E3 使用相同动作标签、20k updates、batch size 4、seed 1000 和 checkpoint 规则完成训练
- [ ] 若要做严格科研对比，重跑 E1/E2/E3 时使用冻结的 80/10/10 source split；本轮是有效的全量 100-episode 训练，`eval_split=0` 表示未在训练中留出验证集
- [x] 旧 E4/Mix-1-300 checkpoint 已完成到 20k；三个视角真机结果 1/10、0/10、0/9，仅作 pilot
- [x] 由原 300 条视角条件样本构建 Mix-1-100，100 个 source 各取一个视角并平衡为 33/33/34
- [x] Mix-1-300 和 All-3 训练输入已就绪
- [ ] 训练 Mix-1-100@20k，使用 seed 1000 和与基线相同的 checkpoint 规则
- [ ] 训练 Mix-1-300@60k，使 300 个 dataset episodes 与 100@20k 保持相同 updates/episode 口径
- [ ] 训练 All-3@20k；确认 feature schema 同时包含三个顶部视角和两个腕部视角
- [ ] 只有 Mix-1-300@60k 单独改善时再补 Single-repeat@60k，排除更多 updates/重复曝光的混杂
- [ ] 补齐每次运行的代码提交和训练曲线；当前只有最终 checkpoint 与超参数，没有中间曲线
- [x] E1/E2/E3 完成训练分布内离线 action sanity check；三个模型都能预测闭合，但手臂关节 MAE 约 0.029–0.032 rad
- [x] 推理改为后台执行、等待期不重发 hold；E4 延后到正式 M 选择和单视角基线之后，捕获区域测量仍单列待办

## P0：配对真机筛查

- [x] E3 M=30 固定 5 布局完整 trace 已保存：正确双角 2/5、双侧抓错位置 1/5、单侧有效 2/5、抬升滑脱 0/5
- [x] E3 M=10 相同桌面标记配对筛查完成：正确双角 2/5、双侧抓错位置 2/5、单侧有效 1/5、滑脱 0/5；L2 改善，L5 向图像上方偏置重复
- [x] E3 M=5 筛查完成：4/5 达 60 s 超时；L2/L3/L5 trace 中未发出闭合指令，主要受同步推理下动作推进过慢混杂，不解释为抓取落点失败
- [x] M=10 为 pilot 候选；旧 M=5 的实际 query rate 仅约 1.12 Hz，结果受当时同步推理实现混杂
- [ ] 核对 M=5/L4 的左右标签：现场称右臂夹住，trace 显示仅 left action/topic 闭合；确认物理臂、操作员视角和 ROS topic 映射
- [x] 30 Hz 重复 hold 已完成真机反证：发布间隔改善，但 L2 从旧 M=10 的成功退化为两次 60 s 未闭合；不得用于正式评估
- [x] 正式 runtime 冻结为后台推理、等待期不重发 joint reference、每 query 仅发布 M 个新动作；M 尚待 5/10/30 正式比较，收尾 smoke 中 L1/L3 可成功夹起
- [ ] L2 持续 timeout；“光照导致策略犹豫”仅为操作员假设。正式测试前冻结顶灯/窗帘状态并记录阴影、反光、自动曝光异常，L2 timeout 仍按失败计数
- [x] 当前 no-hold runtime 下完成 E1/E2/E3 的 M=10/20/30 各 10 次初筛；后续比较冻结 M=20
- [x] E3 checkpoint 换 D435i1/D435i2 各做 5 次 OOD smoke；两组均为 0/5
- [ ] Mix-1-100@20k 在 D435i1、D435i2、Orbbec 三个部署视角下各 10 次
- [ ] Mix-1-300@60k 在 D435i1、D435i2、Orbbec 三个部署视角下各 10 次
- [ ] All-3@20k 固定同时输入三台顶部相机，完成 10 次真机探索
- [x] 冻结五布局定义：`L1=C`，`L2/L3` 为 Orbbec 图像左/右移 30 mm，`L4/L5` 为图像上/下移 30 mm；保持朝向和平整度不变

- [ ] 预先冻结毛巾方向、位置、褶皱和目标角的布局编号
- [ ] 每个主要条件至少 20 次，使用相同布局并随机化方法执行顺序
- [ ] 主要终点：双侧指定材料角抬升 10 cm 并保持 3 s 的成功率及 95% 置信区间
- [ ] 机制指标：左右闭合误差、双角进入物理捕获区域比例、左右/双角夹持率和抬升保持率
- [ ] 人工复核成功标签与失败类型；自动标签不直接作为最终真值
- [ ] 正式 trial 增加 lighting note：顶灯/窗帘状态、明显阴影/反光及自动曝光异常；未做控光配对前不声称 L2 因光照失败
- [ ] 分别报告 E4 在三个部署外部视角上的性能，不只报告合并平均值

## Go/No-Go

- [ ] Mix-1-100@20k 改善：说明固定样本数/updates 下视角多样性有探索性收益，补配对样本确认
- [ ] 只有 Mix-1-300@60k 改善：先做 Single-repeat@60k，不能把更多曝光直接归因于多视角
- [ ] 只有 All-3@20k 改善：做逐相机 mask、错帧和遮挡干预，验证推理期互补来源
- [ ] 三组均无可靠提升或失败机制不变：停止 Random-2、跨视角 loss 和蒸馏，转向示教、反馈、接触与控制方法
- [ ] 只有多视角收益与闭合误差/不确定度下降一致时，才进入跨视角材料点一致性与单视角蒸馏

## 仍需补齐的基础测量

- [ ] 测量真实夹爪捕获区域 `C(e_x,e_y,e_z,e_yaw)`，替代“角点附近 1–2 cm”的主观阈值
- [ ] 记录 prediction horizon `K`、executed steps per query `M`、query/control frequency、temporal ensemble 和端到端延迟
- [ ] 在 50/30/15 mm 阶段做 late-perturbation 配对实验，测响应延迟和误差收缩率 `rho`

## 历史记录（不再作为当前门槛）

- 2026-08-26 的 40 条 approach-only 模型 `test1/020000` 仅证明旧 pipeline 能产生粗粒度跟随现象；不代表直接抓角成功。
- 旧的采集启动、ROS 预检、转换器和控制侧待办已移出 ACT；对应实现与运行证据应在 Physical AI Runtime 维护。
