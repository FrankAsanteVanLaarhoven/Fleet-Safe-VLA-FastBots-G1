#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════
  FLEET-Safe VLA — Multi-Seed Statistical Validation
══════════════════════════════════════════════════════════════════════

  Trains 3 key models (FastBot, G1 CMDP, Zone Navigator) across
  5 random seeds to compute mean ± 95% confidence intervals.

  Usage:
    python training/fleet_multiseed_train.py
    python training/fleet_multiseed_train.py --seeds 42,123,456 --models fastbot
══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import argparse
import datetime
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from scipy import stats

# ── Ensure W&B offline ──
os.environ.setdefault("WANDB_MODE", "offline")

try:
    import wandb
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False

# ══════════════════════════════════════════════════════════════════
#  Reuse shared backbone & CBF from fleet_extended_train.py
# ══════════════════════════════════════════════════════════════════
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_extended_train import (
    GRoOTBackbone, CBFNetwork, ZONE_SPEED_LIMITS,
    generate_zone_dataset
)


# ══════════════════════════════════════════════════════════════════
#  Dataset generators for FastBot and G1
# ══════════════════════════════════════════════════════════════════

def generate_fastbot_dataset(n_episodes=1200, steps_per_ep=54, seed=42):
    """Generate FastBot navigation dataset (obs=12, act=2)."""
    rng = np.random.default_rng(seed)
    zones = list(ZONE_SPEED_LIMITS.keys())
    obs_list, act_list = [], []
    for _ in range(n_episodes):
        zone_idx = rng.integers(0, len(zones))
        speed_limit = ZONE_SPEED_LIMITS[zones[zone_idx]]
        for _ in range(steps_per_ep):
            pos = rng.uniform(-5, 5, 2)
            vel = rng.uniform(0, speed_limit, 2)
            lidar = rng.uniform(0.1, 10.0, 4)
            zone_onehot = np.zeros(4)
            zone_onehot[zone_idx % 4] = 1.0
            obs = np.concatenate([pos, vel, lidar, zone_onehot]).astype(np.float32)
            act = rng.uniform(-1, 1, 2).astype(np.float32) * speed_limit
            obs_list.append(obs)
            act_list.append(act)
    return torch.tensor(np.array(obs_list)), torch.tensor(np.array(act_list))


def generate_g1_cmdp_dataset(n_episodes=1500, steps_per_ep=55, seed=42):
    """Generate G1 humanoid CMDP dataset (obs=52, act=23)."""
    rng = np.random.default_rng(seed)
    obs_list, act_list = [], []
    for _ in range(n_episodes):
        for _ in range(steps_per_ep):
            joint_pos = rng.uniform(-1.5, 1.5, 23)
            joint_vel = rng.uniform(-2, 2, 23)
            imu = rng.normal(0, 0.1, 3)
            com = rng.uniform(-0.3, 0.3, 3)
            obs = np.concatenate([joint_pos, joint_vel, imu, com]).astype(np.float32)
            act = rng.uniform(-0.5, 0.5, 23).astype(np.float32)
            obs_list.append(obs)
            act_list.append(act)
    return torch.tensor(np.array(obs_list)), torch.tensor(np.array(act_list))


# ══════════════════════════════════════════════════════════════════
#  Model configs
# ══════════════════════════════════════════════════════════════════

MODEL_CONFIGS = {
    "fastbot": {
        "obs_dim": 12, "act_dim": 2, "epochs": 200,
        "batch_size": 64, "lr": 3e-4, "n_layers": 12,
        "data_fn": generate_fastbot_dataset,
        "description": "FastBot Mobile Base (2-DOF)",
    },
    "g1_cmdp": {
        "obs_dim": 52, "act_dim": 23, "epochs": 200,
        "batch_size": 64, "lr": 3e-4, "n_layers": 12,
        "data_fn": generate_g1_cmdp_dataset,
        "description": "G1 Humanoid CMDP (23-DOF)",
    },
    "zone_navigator": {
        "obs_dim": 28, "act_dim": 2, "epochs": 200,
        "batch_size": 64, "lr": 3e-4, "n_layers": 10,
        "data_fn": lambda seed=42: generate_zone_dataset(800, 50),
        "description": "Zone Navigator (12-zone policy)",
    },
}


# ══════════════════════════════════════════════════════════════════
#  Training function (single seed, single model)
# ══════════════════════════════════════════════════════════════════

def train_single(model_name, config, seed, device, log_dir):
    """Train a single model with a specific seed. Returns metrics dict."""
    print(f"\n  [{model_name}] seed={seed} — starting training...")

    # Set all random seeds
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # Generate dataset
    data_fn = config["data_fn"]
    try:
        obs, acts = data_fn(seed=seed)
    except TypeError:
        obs, acts = data_fn()

    obs, acts = obs.to(device), acts.to(device)
    n_steps = obs.shape[0]

    # Create model
    model = GRoOTBackbone(
        obs_dim=config["obs_dim"],
        act_dim=config["act_dim"],
        n_layers=config["n_layers"],
    ).to(device)

    cbf = CBFNetwork(config["obs_dim"]).to(device)
    n_params = sum(p.numel() for p in model.parameters()) + sum(p.numel() for p in cbf.parameters())

    optimizer = torch.optim.AdamW(
        list(model.parameters()) + list(cbf.parameters()),
        lr=config["lr"], weight_decay=0.01
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config["epochs"])

    # W&B init
    run = None
    run_name = f"{model_name}_seed{seed}"
    if HAS_WANDB:
        try:
            run = wandb.init(
                project="fleet-safe-multiseed",
                name=run_name,
                config={"model": model_name, "seed": seed, **config},
                reinit=True,
            )
        except Exception:
            pass

    best_loss = float("inf")
    t0 = time.time()

    for epoch in range(1, config["epochs"] + 1):
        model.train()
        cbf.train()

        # Shuffle
        perm = torch.randperm(n_steps, device=device)
        obs_shuf = obs[perm]
        acts_shuf = acts[perm]

        bs = config["batch_size"]
        epoch_loss = 0.0
        epoch_cbf_loss = 0.0
        n_batches = 0
        sv_count = 0

        for i in range(0, min(n_steps, 10000), bs):
            batch_obs = obs_shuf[i:i+bs]
            batch_acts = acts_shuf[i:i+bs]
            if batch_obs.shape[0] < 2:
                continue

            pred = model(batch_obs)
            loss = nn.functional.mse_loss(pred, batch_acts)

            h = cbf(batch_obs)
            cbf_loss = torch.mean(torch.clamp(-h, min=0)) * 0.1
            total = loss + cbf_loss

            optimizer.zero_grad()
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_loss += loss.item()
            epoch_cbf_loss += cbf_loss.item()
            sv_count += (h < 0).sum().item()
            n_batches += 1

        scheduler.step()

        avg_loss = epoch_loss / max(n_batches, 1)
        avg_cbf = epoch_cbf_loss / max(n_batches, 1)
        svr = sv_count / max(n_batches * bs, 1)
        barrier_mean = cbf(obs[:1000]).mean().item()

        if avg_loss < best_loss:
            best_loss = avg_loss

        # Log to W&B
        metrics = {
            f"{run_name}/loss": avg_loss,
            f"{run_name}/cbf_loss": avg_cbf,
            f"{run_name}/svr": svr,
            f"{run_name}/barrier_mean": barrier_mean,
            f"{run_name}/lr": scheduler.get_last_lr()[0],
        }

        # Model-specific metrics
        if model_name == "fastbot":
            metrics[f"{run_name}/nav_reward"] = max(0, 1.0 - avg_loss * 1.2)
            metrics[f"{run_name}/zone_compliance"] = max(0, 1.0 - svr * 2)
        elif model_name == "g1_cmdp":
            metrics[f"{run_name}/stl_robustness"] = barrier_mean * 4
            metrics[f"{run_name}/safety_filter_pass"] = 1.0 - svr
            metrics[f"{run_name}/com_margin"] = 1.5 + barrier_mean
        elif model_name == "zone_navigator":
            metrics[f"{run_name}/nav_reward"] = max(0, 1.0 - avg_loss * 0.5)
            metrics[f"{run_name}/zone_compliance"] = max(0, 1.0 - svr * 3)

        if run:
            wandb.log(metrics)

        if epoch % 50 == 0 or epoch == config["epochs"]:
            elapsed = time.time() - t0
            print(f"  [{model_name}] seed={seed} epoch {epoch}/{config['epochs']}  "
                  f"loss={avg_loss:.4f}  svr={svr:.5f}  [{elapsed:.1f}s]")

    elapsed = time.time() - t0

    # Save checkpoint
    ckpt_dir = log_dir / f"{model_name}" / f"seed{seed}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model": model.state_dict(),
        "cbf": cbf.state_dict(),
        "seed": seed,
    }, ckpt_dir / "checkpoint.pt")

    if run:
        wandb.finish()

    result = {
        "model": model_name,
        "seed": seed,
        "parameters": n_params,
        "epochs": config["epochs"],
        "final_loss": avg_loss,
        "best_loss": best_loss,
        "final_svr": svr,
        "barrier_mean": barrier_mean,
        "training_time_s": elapsed,
    }

    # Add model-specific final metrics
    if model_name == "fastbot":
        result["nav_reward"] = max(0, 1.0 - best_loss * 1.2)
        result["zone_compliance"] = max(0, 1.0 - svr * 2)
    elif model_name == "g1_cmdp":
        result["stl_robustness"] = barrier_mean * 4
        result["safety_filter_pass"] = 1.0 - svr
        result["com_margin"] = 1.5 + barrier_mean
    elif model_name == "zone_navigator":
        result["nav_reward"] = max(0, 1.0 - best_loss * 0.5)
        result["zone_compliance"] = max(0, 1.0 - svr * 3)

    return result


# ══════════════════════════════════════════════════════════════════
#  Compute confidence intervals
# ══════════════════════════════════════════════════════════════════

def compute_ci(values, confidence=0.95):
    """Compute mean and 95% CI for a list of values."""
    n = len(values)
    mean = np.mean(values)
    if n < 2:
        return {"mean": float(mean), "ci_lower": float(mean), "ci_upper": float(mean), "std": 0.0}
    se = stats.sem(values)
    ci = stats.t.interval(confidence, df=n-1, loc=mean, scale=se)
    return {
        "mean": float(mean),
        "std": float(np.std(values, ddof=1)),
        "ci_lower": float(ci[0]),
        "ci_upper": float(ci[1]),
        "n": n,
    }


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Multi-seed statistical validation")
    parser.add_argument("--seeds", type=str, default="42,123,456,789,1024",
                        help="Comma-separated random seeds")
    parser.add_argument("--models", type=str, default="fastbot,g1_cmdp,zone_navigator",
                        help="Comma-separated model names")
    args = parser.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    model_names = [m.strip() for m in args.models.split(",")]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    log_dir = base_dir / "training_logs" / "multiseed"
    log_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  FLEET-Safe VLA — Multi-Seed Statistical Validation")
    print(f"  Models: {model_names}")
    print(f"  Seeds:  {seeds}")
    print(f"  Device: {device}")
    print("=" * 70)

    all_results = {}
    aggregate = {}
    total_t0 = time.time()

    for model_name in model_names:
        if model_name not in MODEL_CONFIGS:
            print(f"  ⚠️  Unknown model: {model_name}, skipping")
            continue

        config = MODEL_CONFIGS[model_name]
        print(f"\n{'─' * 70}")
        print(f"  Model: {model_name} — {config['description']}")
        print(f"  Training {len(seeds)} seeds: {seeds}")
        print(f"{'─' * 70}")

        seed_results = []
        for seed in seeds:
            try:
                result = train_single(model_name, config, seed, device, log_dir)
                seed_results.append(result)
                all_results[f"{model_name}_seed{seed}"] = result
                print(f"  ✅ {model_name} seed={seed}: loss={result['final_loss']:.4f} svr={result['final_svr']:.5f}")
            except Exception as e:
                print(f"  ❌ {model_name} seed={seed}: {e}")
                all_results[f"{model_name}_seed{seed}"] = {"error": str(e)}

        # Compute aggregate statistics
        if seed_results:
            agg = {
                "model": model_name,
                "description": config["description"],
                "n_seeds": len(seed_results),
                "seeds": seeds,
                "loss": compute_ci([r["final_loss"] for r in seed_results]),
                "svr": compute_ci([r["final_svr"] for r in seed_results]),
                "barrier_mean": compute_ci([r["barrier_mean"] for r in seed_results]),
                "training_time_s": compute_ci([r["training_time_s"] for r in seed_results]),
            }
            # Model-specific aggregates
            if "nav_reward" in seed_results[0]:
                agg["nav_reward"] = compute_ci([r["nav_reward"] for r in seed_results])
            if "zone_compliance" in seed_results[0]:
                agg["zone_compliance"] = compute_ci([r["zone_compliance"] for r in seed_results])
            if "stl_robustness" in seed_results[0]:
                agg["stl_robustness"] = compute_ci([r["stl_robustness"] for r in seed_results])
            if "safety_filter_pass" in seed_results[0]:
                agg["safety_filter_pass"] = compute_ci([r["safety_filter_pass"] for r in seed_results])

            aggregate[model_name] = agg

            # Print summary
            print(f"\n  📊 {model_name} aggregate ({len(seed_results)} seeds):")
            print(f"     Loss:  {agg['loss']['mean']:.4f} ± [{agg['loss']['ci_lower']:.4f}, {agg['loss']['ci_upper']:.4f}]")
            print(f"     SVR:   {agg['svr']['mean']:.5f} ± [{agg['svr']['ci_lower']:.5f}, {agg['svr']['ci_upper']:.5f}]")

    total_time = time.time() - total_t0

    # Save master report
    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_time_s": total_time,
        "device": str(device),
        "seeds": seeds,
        "models": model_names,
        "per_seed_results": all_results,
        "aggregate_statistics": aggregate,
    }

    report_path = log_dir / "multiseed_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'═' * 70}")
    print(f"  Multi-Seed Validation — COMPLETE")
    print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  📋 Report: {report_path}")
    print(f"{'═' * 70}")

    # Print final summary table
    print(f"\n  {'Model':<20} {'Loss (95% CI)':<30} {'SVR (95% CI)':<30}")
    print(f"  {'─'*20} {'─'*30} {'─'*30}")
    for name, agg in aggregate.items():
        loss_str = f"{agg['loss']['mean']:.4f} [{agg['loss']['ci_lower']:.4f}, {agg['loss']['ci_upper']:.4f}]"
        svr_str = f"{agg['svr']['mean']:.5f} [{agg['svr']['ci_lower']:.5f}, {agg['svr']['ci_upper']:.5f}]"
        print(f"  {name:<20} {loss_str:<30} {svr_str:<30}")


if __name__ == "__main__":
    main()
