# ECE Sizing Calculator

**Elastic Cloud Enterprise Deployment Planner** — a single-file, browser-based sizing calculator for planning ECE deployments. Built and maintained by Expedient Technology Solutions.

🔗 **Live app:** [ece-sizer.pplx.app](https://ece-sizer.pplx.app)

---

## Overview

The ECE Sizing Calculator takes your data characteristics (ingest rate, retention, use case) and outputs RAM, storage, node counts, and shard health guidance aligned with Elastic's published best practices. No backend, no build tools — a single `index.html` file.

## Features

- **Use case presets** — SIEM, APM, Security Analytics, Enterprise Search, Custom
- **Architecture presets** — Elastic Standard (3-tier HA), Expedient Optimized, Minimal (dev/test)
- **Multi-tier sizing** — Hot / Warm / Cold / Frozen tiers with per-tier RAM:storage ratios
- **ILM rollover modeling** — Age-based and size-based rollover conditions
- **Shard model** — Per-tier shard ceilings (1,000/node hard limit, ES 8.3+), cluster-wide health banner, actionable recommendations
- **ECE instance snapping** — Automatically snaps node RAM to valid ECE `data.default` sizes (1, 2, 4, 8, 16, 32, 64 GB)
- **Allocator overhead** — Models 12 GB ECE control plane overhead per allocator host
- **CPU ingest hint** — Planning heuristic for hot tier vCPU adequacy
- **Frozen tier cache health** — Validates cache % against Elastic's 5–10% guidance
- **Export / Import JSON** — Full configuration round-trip
- **Share URL** — Encodes configuration in URL parameters for quick handoff
- **Dark / Light mode** — Respects system preference
- **Version badge** — Visible version number in header

## Usage

Open `index.html` in any modern browser — no installation or build step required.

```bash
open index.html
```

Or serve locally:

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

## Formula Reference

All formulas are documented in the [ECE Sizing Calculator User Guide](./ECE_Sizing_Calculator_User_Guide.pdf) included in this repository, and backed by official Elastic documentation:

| Formula | Source |
|---|---|
| RAM:storage ratios (hot 1:30, warm/cold 1:160, frozen 1:1500) | [Elastic hardware recommendations](https://www.elastic.co/guide/en/cloud/current/ec-hardware.html) |
| ECE instance sizes (1,2,4,8,16,32,64 GB) | [ECE instance configurations](https://www.elastic.co/guide/en/cloud-enterprise/current/ece-instance-configurations.html) |
| ECE control plane overhead (12 GB/allocator) | [ECE allocator planning](https://www.elastic.co/guide/en/cloud-enterprise/current/ece-allocators.html) |
| Target shard size (10–50 GB) | [Size your shards](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html) |
| Shard ceiling (1,000/node) | [cluster.max_shards_per_node](https://www.elastic.co/guide/en/elasticsearch/reference/current/misc-cluster-settings.html#cluster-max-shards-per-node) |
| Disk watermark headroom (15%) | [Disk-based shard allocation](https://www.elastic.co/guide/en/elasticsearch/reference/current/disk-usage-watermark.html) |
| JVM heap cap (31 GB) | [Heap sizing](https://www.elastic.co/guide/en/elasticsearch/reference/current/advanced-configuration.html#set-jvm-heap-size) |
| Frozen cache guidance (5–10%) | [Frozen tier](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-tiers.html#frozen-tier) |

## Version History

| Version | Changes |
|---|---|
| v1.0.9 | Fixed coldRatio default (1500→160), frozenRatio (8500→1500), ECE instance sizes ({15,29,58,60}→{16,32,64}), ECE control plane overhead (6→12 GB), shard ceiling model (20/GB-heap→1,000/node), cluster shard limit (fixed 50k→1,000×nodes); tooltip and heuristic caveats added |
| v1.0.8 | ILM rollover toggle (age-based vs size-based), active hot indices hint |
| v1.0.7 | Infrastructure defaults updated to match Expedient ECE environment (14 allocators, 1412 GB RAM) |
| v1.0.6 | Advanced section grouped into 5 labeled categories |
| v1.0.5 | JS singleton tooltip engine with viewport clamping; version badge added |
| v1.0.4 | Formula critique fixes: ECE instance snapping, per-tier overhead multipliers, master RAM scaling, frozen cache sanity, snapshot model toggle, CPU hint, allocator overhead KPI |
| v1.0.3 | Import JSON button; full-fidelity export/import round-trip |
| v1.0.2 | Shard model: per-tier ceilings, utilization bars, cluster health banner, recommendations panel |
| v1.0.1 | Fixed Security Analytics, Enterprise Search, and Custom presets |
| v1.0.0 | Initial release |

## Files

| File | Description |
|---|---|
| `index.html` | Single-file application — all HTML, CSS, and JS |
| `ECE_Sizing_Calculator_User_Guide.pdf` | 9-section client-facing user guide with formula reference and Elastic source citations |
| `README.md` | This file |

## License

Internal tool — Expedient Technology Solutions. Not licensed for redistribution.
