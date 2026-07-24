# Quantinvesting

基于 **Tushare + Qlib** 的本地 AI 多因子量化研究项目。

第一阶段目标：跑通「数据 → 因子 → 模型 → 回测」完整闭环，实现招商证券端到端动态 Alpha（MLP）思路；西部证券多因子框架作为预处理、因子检验与组合构建的流程骨架。后续再迭代因子库、模型与组合优化。

**项目约定：每个基本面因子进入多因子 / MLP 之前，必须先做单因子测试**（预处理 → IC/分组/回归 → 筛选）。学习说明见 [`docs/single_factor_test.md`](docs/single_factor_test.md)。

> 当前进度：数据管线骨架已搭好（下载 / 清洗 / QA / Qlib dump）；单因子测试为学习骨架。默认 **dry-run**，不会真正请求接口。

---

## 研究依据

| 研报 | 角色 |
|------|------|
| 招商证券《端到端的动态 Alpha 模型》 | 核心 Alpha：截面 MLP、正交惩罚、MSE/IC/CCC loss |
| 西部证券《量化多因子选股框架》 | 流程：预处理 → 单因子检验 → 收益预测 → 组合构建 |

本地环境建议：

- Mac M 系列 / 16GB 内存可用（第一版 MLP 很轻）
- Conda 环境 `quantinvesting`，Python **3.12**（勿用 3.13）
- Tushare **5000 积分** 足够日频 + 财务 VIP 接口

---

## 仓库结构

```text
Quantinvesting/
├── configs/
│   └── data.yaml                 # 下载窗口、限速、清洗与 label 默认参数
├── data/
│   ├── raw/                      # Tushare 原始落盘（只追加，不改写）
│   │   ├── meta/                 # stock_basic / trade_cal / 行业
│   │   ├── daily/                # 按年/交易日 parquet
│   │   ├── daily_basic/
│   │   ├── adj_factor/
│   │   ├── fina/                 # 财务 VIP，按报告期
│   │   └── index/
│   ├── clean/                    # 清洗后面板
│   ├── qlib/                     # Qlib provider 数据
│   └── meta/                     # download_log.json 等
├── docs/
│   └── single_factor_test.md      # 西部单因子测试学习笔记（基本面必读）
├── src/quantinvesting/
│   ├── data/
│   │   ├── download/             # 分层下载器
│   │   ├── clean/                # 清洗 pipeline + QA
│   │   └── qlib_dump/            # dump 到 Qlib（骨架）
│   ├── factors/
│   │   ├── fundamental_specs.py  # 基本面候选因子清单
│   │   └── single_test.py        # 单因子测试骨架
│   └── utils/                    # 配置、限速、断点日志、token
├── scripts/
│   └── pipeline.py               # CLI 入口
├── qlib/                         # Microsoft Qlib 源码（本地 editable 安装）
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## 环境准备

### 1. Conda 环境

```bash
conda activate quantinvesting
# 若尚未创建：
# conda create -n quantinvesting python=3.12 -y
# conda activate quantinvesting
```

### 2. 安装本项目依赖

```bash
cd /path/to/Quantinvesting
pip install -r requirements.txt
# 或
pip install -e .
```

### 3. 安装 Qlib（macOS 如遇 C++ 头文件报错）

```bash
cd qlib
export SDKROOT=$(xcrun --sdk macosx --show-sdk-path)
export CPLUS_INCLUDE_PATH="$SDKROOT/usr/include/c++/v1"
pip install -e ".[dev]"
cd ..
```

### 4. 配置 Tushare Token

```bash
cp .env.example .env
# 编辑 .env，填入：
# TUSHARE_TOKEN=你的token
```

---

## 快速使用

所有命令默认 **dry-run**（只打印计划，不请求 API、不写大数据）。真正执行时加 `--execute`。

```bash
# 预览
python scripts/pipeline.py meta
python scripts/pipeline.py daily
python scripts/pipeline.py fina
python scripts/pipeline.py index
python scripts/pipeline.py all-download

# 真正下载（建议先 meta，再 daily / fina）
python scripts/pipeline.py --execute meta
python scripts/pipeline.py --execute daily
python scripts/pipeline.py --execute fina
python scripts/pipeline.py --execute index

# 清洗 / 质检 / dump（目前多为骨架）
python scripts/pipeline.py clean
python scripts/pipeline.py qa
python scripts/pipeline.py dump-qlib
```

自定义配置：

```bash
python scripts/pipeline.py --config configs/data.yaml daily
```

---

## 数据设计

### 下载原则

1. **行情按交易日全市场拉取**（`daily` / `daily_basic` / `adj_factor`），不要按股票循环。
2. **财务用 VIP 接口按报告期拉取**（`fina_indicator_vip` 等），一季一次拿全市场。
3. **原始数据只追加落盘** 到 `data/raw/`，清洗结果写 `data/clean/`。
4. **断点续传**：`data/meta/download_log.json` 记录已完成的 `api:key`。
5. **限速 + 重试**：默认 `sleep_seconds=0.15`，失败指数退避重试 3 次。

### 分层

| 层级 | 内容 | 更新 |
|------|------|------|
| L0 Meta | 股票列表、交易日历、行业分类 | 低频 |
| L1 Daily | 日线、每日指标、复权因子 | 按日增量 |
| L2 Financial | 财务指标 / 三表 VIP | 按报告期 |
| L3 Index | 指数行情、成分权重 | 日/月 |

默认研究窗口见 `configs/data.yaml`：`start_date: "20180101"`。

### 清洗原则（规划）

1. 用 `adj_factor` 复权；label 对齐招商：**T+1～T+21 复权 VWAP 收益**，约 20 日调仓。
2. 财务按 **公告日 `ann_date` / `f_ann_date`** 对齐到交易日，禁止用报告期当可用日（防未来函数）。
3. 股票池：剔 ST、上市未满约 3 个月、停牌等。
4. 因子预处理：截面 3 倍 MAD → z-score → 市值/行业中性化 → 缺失填充。

---

## 配置说明

主要文件：[`configs/data.yaml`](configs/data.yaml)

| 配置项 | 含义 |
|--------|------|
| `download.start_date` / `end_date` | 下载区间（`end_date: null` 表示今天） |
| `download.sleep_seconds` | API 调用间隔 |
| `download.stock_pool` | 后续选股池（`csi500` 等） |
| `clean.mad_n` | MAD 去极值倍数 |
| `clean.exclude.listed_days_min` | 次新股最少上市交易日 |
| `label.horizon_days` | 预测收益窗口 |

---

## 单因子测试（基本面优先）

正确顺序：

```text
基本面因子定义（经济含义 + 方向）
  → 预处理（MAD / zscore / 行业·市值中性）
  → 西部四法：RankIC·ICIR / 分组 / 双变量 / 回归
  → 筛选（有效 + 低冗余）
  → 才进入多因子或 MLP
```

- 学习文档：[`docs/single_factor_test.md`](docs/single_factor_test.md)  
- 候选清单：`src/quantinvesting/factors/fundamental_specs.py`  
- 测试骨架：`src/quantinvesting/factors/single_test.py`  

不要跳过单测直接把财务字段塞进 AI 模型。

---

## 路线图

- [x] 项目骨架：目录、配置、CLI、下载器 / 清洗 / dump 占位
- [x] 单因子测试学习文档 + 基本面候选清单骨架
- [ ] 执行 meta + daily + fina 首轮下载
- [ ] 实现清洗：复权、PIT 财务、宇宙过滤、因子预处理、label
- [ ] 实现单因子测试（逐个基本面因子出报告）
- [ ] Dump 到 Qlib provider
- [ ] 线性基准 + 招商风格 MLP（正交惩罚 / IC loss）
- [ ] 回测与 IC / 分组 / 多头净值报告
- [ ] （后续）组合优化、更多因子、滚动训练自动化

---

## 注意事项

- Token 只放在 `.env`，不要提交到 Git（已在 `.gitignore`）。
- `data/raw`、`data/clean`、`data/qlib` 默认不入库，体积大且可重建。
- 积分是调用门槛，**不消耗**；5000 积分支持常规日频与财务 VIP，分钟线等需单独开通。
- 第一版追求流程跑通，不追求复现研报精确数值。

---

## License

本仓库研究代码与配置遵循项目后续约定；`qlib/` 目录遵循 [Microsoft Qlib](https://github.com/microsoft/qlib) 自身许可证。研报内容版权归原发布机构所有，仅供学习研究参考。
