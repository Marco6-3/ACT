# 2026-08-29 三视角数据最终验收

## 结论

当前数据结论为 **PASS / GO**。原始 source `episode_000068`、`episode_000069`、`episode_000070`
继续因 MCAP 截断而隔离；补采的 `episode_000101`、`episode_000102` 已通过源文件完整性、转换、全量
解码和视觉抽检。三份 LeRobot 数据现有恰好 100 条有效 source，并已冻结 80/10/10 split。

本次只完成数据交接，没有启动 E1/E2/E3 训练。

## 有效数据范围与机器验收

有效 source index 为 `0–67, 71–102`，共 100 条。机器可读报告见
[`five_camera_v1/data_acceptance_2026-08-29.json`](./five_camera_v1/data_acceptance_2026-08-29.json)。

| 数据集 | episodes | frames | manifest | data parquet | episode parquet | 三路视频/路 |
|---|---:|---:|---:|---:|---:|---:|
| `pick_corner_orbbec` | 100 | 35,474 | 100 | 100 | 100 | 100 |
| `pick_corner_d435i1` | 100 | 35,474 | 100 | 100 | 100 | 100 |
| `pick_corner_d435i2` | 100 | 35,474 | 100 | 100 | 100 | 100 |

验收程序对全部 100 组配对 source 做了以下检查，错误数为 0：

- source ID、source fingerprint、episode 帧数、30 Hz 和同步 topic 集合一致；
- `state`、`action`、`timestamp`、`frame_index` 的 Arrow 内容哈希跨三份数据一致；
- 左右腕部 MP4 的 SHA-256 跨三份数据一致；
- 输入 key 固定为 `top + left_wrist + right_wrist`，图像为 `480×640×3`，state/action 为 14 维；
- 900 个 MP4 全部逐帧解码，解码帧数与 manifest 一致，分辨率均为 `640×480`，帧率均为 30 Hz；
- 所有候选项均为人工确认的 `accepted_success`、`stable_corner_grasp_success=true`、`human_verified=true`。

抽取 source `0/49/100` 的三路 top 中间帧做视觉复核，未见错相机、黑帧、翻转或 RGB/BGR
通道颠倒；各视角内容和相机位姿符合预期。联系图见
[`five_camera_v1/data_acceptance_contact_sheet_2026-08-29.jpg`](./five_camera_v1/data_acceptance_contact_sheet_2026-08-29.jpg)。

补采 source `101/102` 的源文件 SHA-256 均通过；五路相机分别写入 `376/314` 帧，两条均为
`result=PASS`、`writer_failed=false`、`total_recorder_drops=0`、无 errors/warnings。转换后分别为
375 帧和 313 帧。三视角中间帧抽检通过，见
[`five_camera_v1/new_sources_101_102_contact_sheet_2026-08-29.jpg`](./five_camera_v1/new_sources_101_102_contact_sheet_2026-08-29.jpg)。

## 损坏 source 与隔离依据

三条 source 的 sidecar 均曾记录 `PASS`、零 recorder drop 且人工标签为成功，但当前 MCAP 的实际
SHA-256 与录制时保存的校验和不一致，读取也在文件尾前遇到不完整 record。因此不能通过重写校验和
或只使用可读前缀来“修复”训练数据。

| source | 录制时 SHA-256 | 当前 SHA-256 | 读取失败位置 | 当前可读相机帧概况 |
|---|---|---|---:|---|
| 68 | `f3bc6b2e…4082bb2` | `5e279e6f…de64c4` | offset 1,098,468,743 | Orbbec/D435i1/D435i2/左腕 170，右腕 169 |
| 69 | `b71e5a61…9d9aa1` | `9d5a4605…7e9b78` | offset 1,060,555,830 | 五路均 164 |
| 70 | `5c3e08da…a765fb` | `8060bae8…8c13d0` | offset 979,242,646 | D435i1/D435i2/左腕 152，Orbbec/右腕 151 |

本机 `/home`、回收站以及已挂载的 `/mnt`、`/media` 未发现这三条 MCAP 的完整备份或副本。

## Orbbec 1280×720 到 640×480

现场预检记录 Orbbec 原始尺寸为 `1280×720`。转换器先按目标 4:3 计算中央宽度
`round(720 × 4 / 3) = 960`，保留水平像素 `x=160…1119`，再以双线性插值缩放到 `640×480`。
因此流程是中央裁切加等比例缩放，不会把 16:9 画面横向压缩成 4:3。

对应的合成测试使用左 160 像素红色、中间 960 像素绿色、右 160 像素蓝色的 1280×720 图像，输出
为全绿色 `480×640`；相关 paired3/归一化测试结果为 `4 passed, 33 deselected`。

## Smoke test：150 写入帧为何转换为 149 帧

smoke 原始记录中五路相机均为 `received=150`、`written=150`、`recorder_drops=0`；三份转换结果均为
149 帧，所有视频也都实际解码为 149 帧。转换器使用五路相机的共同时间窗口：

```text
start = max(each stream first timestamp)
end = min(each stream last timestamp)
frame_count = floor((end - start) / (1e9 / 30)) + 1
```

150 个 30 Hz 样本只有 149 个采样间隔。五路异步到达造成共同窗口略短于完整的 149 个周期，因此合法
目标时间点为 149 个（`0…4.933333 s`）。这是同步边界裁剪，不是写入丢帧；原始计数、零 drop、共同
state/action/timestamp 以及输出视频解码数彼此一致。

## 冻结 split 与交接

[`five_camera_v1/source_split.json`](./five_camera_v1/source_split.json) 使用固定 seed `20260829`，按
source episode 一次性冻结 train/validation/test = 80/10/10。三个相机数据集的同一 source 使用完全
相同的 dataset episode index；split 之间无重叠，全集恰好覆盖 100 条。

训练 split 的三套数据均为 80 episodes、28,103 frames。使用 PyAV 实际加载首个训练样本通过：三路
图像张量均为 `3×480×640`，state/action 均为 14 维。训练未启动，输出目录和 checkpoint 均未创建。
