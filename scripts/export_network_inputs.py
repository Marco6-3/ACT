#!/usr/bin/env python3
"""Export images from the same dataset and preprocessing path used for ACT training."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from PIL import Image, ImageDraw
from torch.utils.data import DataLoader, Subset

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.policies import make_pre_post_processors
from lerobot.policies.act.configuration_act import ACTConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--count", type=int, default=20)
    return parser.parse_args()


def evenly_spaced_indices(length: int, count: int) -> list[int]:
    if not 1 <= count <= length:
        raise ValueError(f"count must be between 1 and {length}, got {count}")
    if count == 1:
        return [0]
    return [round(i * (length - 1) / (count - 1)) for i in range(count)]


def tensor_to_image(tensor: torch.Tensor) -> Image.Image:
    array = (
        tensor.detach()
        .cpu()
        .clamp(0, 1)
        .mul(255)
        .round()
        .to(torch.uint8)
        .permute(1, 2, 0)
        .numpy()
    )
    return Image.fromarray(array, mode="RGB")


def make_contact_sheet(panels: list[tuple[str, list[tuple[str, Image.Image]]]]) -> Image.Image:
    image_width, image_height = 240, 180
    label_height = 22
    panel_width = 3 * image_width
    panel_height = image_height + label_height
    panel_columns = 2
    panel_rows = (len(panels) + panel_columns - 1) // panel_columns
    sheet = Image.new("RGB", (panel_columns * panel_width, panel_rows * panel_height), "white")
    draw = ImageDraw.Draw(sheet)

    for panel_index, (sample_label, images) in enumerate(panels):
        panel_x = panel_index % panel_columns * panel_width
        panel_y = panel_index // panel_columns * panel_height
        draw.text((panel_x + 4, panel_y + 4), sample_label, fill="black")
        for camera_index, (camera_name, image) in enumerate(images):
            resized = image.resize((image_width, image_height), Image.Resampling.LANCZOS)
            image_x = panel_x + camera_index * image_width
            image_y = panel_y + label_height
            sheet.paste(resized, (image_x, image_y))
            draw.rectangle((image_x, image_y, image_x + 105, image_y + 16), fill="white")
            draw.text((image_x + 2, image_y + 2), camera_name, fill="black")
    return sheet


def main() -> None:
    args = parse_args()
    checkpoint = args.checkpoint.resolve()
    output_dir = args.output_dir.resolve()
    train_config = json.loads((checkpoint / "train_config.json").read_text())
    dataset_config = train_config["dataset"]
    policy_config = ACTConfig.from_pretrained(checkpoint, local_files_only=True)

    dataset_root = Path(dataset_config["root"])
    dataset_info = json.loads((dataset_root / "meta" / "info.json").read_text())
    fps = dataset_info["fps"]
    delta_timestamps = {"action": [step / fps for step in policy_config.action_delta_indices]}
    dataset = LeRobotDataset(
        repo_id=dataset_config["repo_id"],
        root=dataset_root,
        delta_timestamps=delta_timestamps,
        tolerance_s=train_config["tolerance_s"],
        video_backend=dataset_config["video_backend"],
        return_uint8=True,
    )

    sample_indices = evenly_spaced_indices(len(dataset), args.count)
    loader = DataLoader(Subset(dataset, sample_indices), batch_size=args.count, shuffle=False, num_workers=0)
    batch = next(iter(loader))
    camera_keys = list(policy_config.image_features)

    for camera_key in camera_keys:
        if batch[camera_key].dtype != torch.uint8:
            raise TypeError(f"Expected uint8 dataloader images for {camera_key}, got {batch[camera_key].dtype}")
        batch[camera_key] = batch[camera_key].to(torch.float32) / 255.0

    # Preserve directly decoded RGB for visualization. The policy receives the same
    # tensors after the checkpoint preprocessor applies mean/std normalization.
    visual_inputs = {camera_key: batch[camera_key].clone() for camera_key in camera_keys}
    preprocessor, _ = make_pre_post_processors(
        policy_cfg=policy_config,
        pretrained_path=str(checkpoint),
    )
    processed_batch = preprocessor(batch)

    output_dir.mkdir(parents=True, exist_ok=True)
    panels: list[tuple[str, list[tuple[str, Image.Image]]]] = []
    manifest_rows: list[dict[str, object]] = []
    for sample_number, dataset_index in enumerate(sample_indices):
        episode_index = int(batch["episode_index"][sample_number].item())
        frame_index = int(batch["frame_index"][sample_number].item())
        timestamp = float(batch["timestamp"][sample_number].item())
        panel_images: list[tuple[str, Image.Image]] = []
        for camera_key in camera_keys:
            camera_name = camera_key.removeprefix("observation.images.")
            image = tensor_to_image(visual_inputs[camera_key][sample_number])
            filename = f"sample_{sample_number:02d}_ep_{episode_index:02d}_frame_{frame_index:04d}_{camera_name}.jpg"
            image.save(output_dir / filename, quality=92)
            normalized = processed_batch[camera_key][sample_number]
            manifest_rows.append(
                {
                    "sample_number": sample_number,
                    "dataset_index": dataset_index,
                    "episode_index": episode_index,
                    "frame_index": frame_index,
                    "timestamp_s": f"{timestamp:.6f}",
                    "camera_key": camera_key,
                    "file": filename,
                    "network_shape": "x".join(map(str, normalized.shape)),
                    "network_dtype": str(normalized.dtype),
                    "normalized_min": f"{normalized.min().item():.6f}",
                    "normalized_max": f"{normalized.max().item():.6f}",
                    "normalized_mean": f"{normalized.mean().item():.6f}",
                    "normalized_std": f"{normalized.std().item():.6f}",
                }
            )
            panel_images.append((camera_name, image))
        panels.append((f"sample {sample_number:02d} | ep {episode_index:02d} frame {frame_index:04d}", panel_images))

    with (output_dir / "manifest.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    summary = {
        "checkpoint": str(checkpoint),
        "dataset_root": str(dataset_root.resolve()),
        "sample_count": args.count,
        "image_count": args.count * len(camera_keys),
        "sample_indices": sample_indices,
        "camera_keys": camera_keys,
        "visualization_stage": "decoded uint8 converted to float32/255, immediately before checkpoint mean/std normalization",
        "processed_device": str(processed_batch[camera_keys[0]].device),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    make_contact_sheet(panels).save(output_dir / "contact_sheet.jpg", quality=92)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
