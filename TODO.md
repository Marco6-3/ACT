# TODO — 课程式 ACT 毛巾折叠

## 已完成

- [x] 完成五路同步数据与 ACT 运行链路验收；
- [x] 完成 E1/E2/E3 与执行步长筛查，定位粗抓取、视角匹配和控制吞吐问题；
- [x] 用 100 条 Orbbec 直接抓角数据训练 `pick_corner_orbbec_150@20k`；
- [x] 用该策略 rollout，并在夹取风险/夹爪偏位时人工接管完成折叠；
- [x] 覆盖红、绿毛巾和偏位困难状态；
- [x] 转换 HIL 数据；当前磁盘口径为 101 episodes、54,791 frames；
- [x] 从 base20k 初始化，在 HIL 数据上微调 10k steps；
- [x] 定性测试达到完整抓取至折叠，多颜色现场表现良好。

## 明天 P0

- [ ] 补齐 HIL episode 的颜色、毛巾实例、布局语义和验收标签；
- [ ] 冻结三个 checkpoint、C/H1–H4、第三颜色未见毛巾、实际 M 和照明；
- [ ] 完成 36 次 base/scratch/fine-tune 配对筛查；
- [ ] 若通过，完成 fine-tune 的 45 次颜色 × 布局验收；
- [ ] 保存所有成功、失败、超时和安全终止，并逐条人工复核；
- [ ] 汇总 Wilson 95% CI、阶段成功率、任务时间、折叠误差和失败类型。



执行顺序和停止条件见 [`docs/NEXT_EXPERIMENTS.md`](./docs/NEXT_EXPERIMENTS.md)。
