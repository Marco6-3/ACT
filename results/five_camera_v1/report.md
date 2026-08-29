# Five-camera v1 report

状态（2026-08-29）：补采 source `101/102` 后，三份单外部视角数据集均达到 100 条有效 source 并通过
全量验收；source `68/69/70` 继续隔离。E1–E4 已使用全部 100 episodes 完成 20,000 steps 全量训练；
该做法对最终部署模型有效，但没有执行已冻结的 80/10/10 科研评估 split。用户定性尝试 E1–E3 后，
三者均能接近目标角，但几乎不能双侧有效抓起。
模型失败诊断见 [`../e1_e3_grasp_failure_diagnosis_2026-08-29.md`](../e1_e3_grasp_failure_diagnosis_2026-08-29.md)，
数据验收详情见 [`../data_acceptance_2026-08-29.md`](../data_acceptance_2026-08-29.md)。

## 数据与模型可追溯性

- 冻结 source：`0–67, 71–102`，共 100 条；损坏 source：`68/69/70`。
- `pick_corner_orbbec`、`pick_corner_d435i1`、`pick_corner_d435i2` 各 100 episodes、35,474 frames。
- 三份数据共 900 个视频均完整解码为 `640×480@30Hz`；机器验收错误数为 0。
- `source_split.json` 已按固定 seed `20260829` 冻结为 train/validation/test = 80/10/10。

## 稳定抓角成功率

100 条冻结 source 均保留人工 `accepted_success`、`stable_corner_grasp_success=true` 和 `human_verified=true` 标签。
E1–E3 只有“几乎不能双侧有效抓起”的定性反馈，尚无逐 trial 结果，因此不能计算成功率或置信区间。

更新：E3-Orbbec M=30 已完成固定五布局筛查。现场人工结果为正确双角 2/5、双侧抓到布但抓错角点 1/5、
单侧有效 2/5，已夹持后滑脱 0/5；由于尚未逐视频核对 10 cm / 3 s，2/5 只记为 provisional。
详见 [`../e3_m30_screening_2026-08-29.md`](../e3_m30_screening_2026-08-29.md)。

同布局 M=10 得到正确双角 2/5、双侧抓错位置 2/5、单侧有效 1/5，双侧捕获率由 3/5 增到 4/5，
但正确双角仍为 2/5。M=5 有 4/5 达 60 s 超时；其中 L2/L3/L5 结束前没有发布闭合指令。同步 GPU
推理令 M=5 实际 query rate 仅约 1.12 Hz，并使动作推进吞吐约为 M=10 的一半，因此不能把 M=5 超时
解释成落点精度下降。当前部署候选为 M=10。详见
[`../e3_m10_m5_screening_2026-08-29.md`](../e3_m10_m5_screening_2026-08-29.md)。

当天执行链路试验表明，以 30 Hz 重复发送最后一条 hold 会使 M=10 行为退化，已从正式候选撤销；当前
候选保留后台推理，但等待期间不重复发布 joint reference。操作员确认 L1/L3 可夹起，最新 L3 trace
双侧闭合且 health PASS；L2 仍 timeout。L2 的光照敏感性只记为待验证假设。下一阶段先完成 E3-Orbbec
M=10 的 20 次正式评估，再用匹配的 E1-D435i1 和 E2-D435i2 checkpoint/topic 做同协议比较。

## 角点闭合误差与失败类型

已进入定性模型筛查，但未保存逐 trial failure taxonomy。离线 action 统计显示所有 100 条成功示教都是
串行闭合：左右首次 `<5 mm` 间隔最小 1.43 s、中位 2.80 s、最大 5.43 s，左先/右先为 57/43。
source `68/69/70` 属于数据文件完整性失败，不计为策略失败样本。

## Mix-1 Go/No-Go

数据完整性门禁为 **GO**，但任务行为门禁改为 **NO-GO**：当前示教时序与同步双抓目标不一致，且 E1–E3
共同暴露出厘米级精度/接触闭环问题。E4 checkpoint 已生成，但在闭合 trace、短 `M` 筛查和物理捕获区域
测量完成前，不用它得出 Mix-1 收益结论。
