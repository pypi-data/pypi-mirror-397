## lidb

### 项目简介
lidb 是一个基于 Polars 的数据管理和分析库，专为金融量化研究设计。它提供了高效的数据存储、查询和表达式计算功能，支持多种时间序列和横截面数据分析操作。

### 功能特性
- **多数据源支持**: 本地 Parquet 存储、MySQL、ClickHouse 等数据库连接
- **高效数据存储**: 基于 Parquet 格式的分区存储机制
- **SQL 查询接口**: 支持标准 SQL 语法进行数据查询
- **表达式计算引擎**: 提供丰富的 UDF 函数库，包括时间序列、横截面、维度等分析函数
- **数据集管理**: 自动化数据补全、历史数据加载和 PIT(Point-in-Time)数据处理
- **数据集管理**: 自动化数据补全、历史数据加载和 PIT(Point-in-Time)数据处理

### 安装
```bash
pip install -U lidb
```

### 快速开始

#### 基础数据操作
```python
import lidb
import polars as pl

df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

# 写入数据
lidb.put(df, "my_table")

# sql 查询
res = lidb.sql("select * from my_table;")
```

#### 数据集使用
```python
import lidb
from lidb import Dataset
import polars as pl

# 定义一个tick级别的高频数据集: 高频成交量
def hft_vol(date: str, num: int) -> pl.DataFrame | pl.LazyFrame | None:
    # 假设上游tick行情表在clickhouse
    quote_query = f"select * from quote where date = '{date}'"
    quote = lidb.read_ck(quote_query, db_conf="databases.ck")
    # 特征计算: 比如过去20根tick的成交量总和, 使用表达式引擎计算
    return lidb.from_polars(quote).sql(f"itd_sum(volume, {num}) as vol_s20")

ds_hft_vol = Dataset(fn=hft_vol, 
                     tb="path/to/hft_vol", 
                     partitions=["num"], 
                     update_time="", # 实时更新
                     by_asset=True, # 根据asset_id进行分区
                    )(num=20)

# 获取历史数据
history_data = ds_hft_vol.get_history(["2023-01-01", "2023-01-02", ...])
```

#### 表达式计算
```python
import lidb

date = "2025-05-15"
quote_query = f"select * from quote where date = '{date}'"
quote = lidb.read_ck(quote_query, db_conf="databases.ck")

qdf = lidb.from_polars(quote)

# 使用 QDF 进行表达式计算
res = qdf.sql(
    "ts_mean(close, 5) as c_m5", 
    "cs_rank(volume) as vol_rank", 
)
```

### 核心模块

#### 数据库操作(`database.py`)
- `put`: 将 `polars.DataFrame` 写入指定表
- `sql`: 执行 `SQL` 查询
- `has`: 检查表是否存在
- `read_mysql`,`write_mysql`: mysql 数据读写
- `read_ck`: clickhouse 数据读取

#### 数据集管理(`dataset.py`)
- `Dataset`: 数据集定义和管理
- `DataLoader`： 数据加载器
- `zoo`: alpha因子数据管理

#### 表达式计算(`qdf/`)
- `QDF`: 表达式数据库
- `Expr`: 表达式解析器
- `UDF 函数库`:
    - `base_udf`: 基础运算函数
    - `ts_udf`: 时间序列函数
    - `cs_udf`: 横截面函数
    - `d_udf`: 日期维度函数
    - `itd_udf`: 日内函数

#### 配置管理(`init.py`)
- 自动创建配置文件
- 支持自定义数据存储路径
- `polars` 线程配置
#### 配置说明
首次运行会在 `~/.config/lidb/settings.toml` 创建配置文件:
```toml
[GLOBAL]
path = "~/lidb"  # 数据存储路径

[POLARS]
max_threads = 32  # Polars 最大线程数
```

### 许可证
本项目采用 MIT 许可证, 请在项目根目录下查看

### 联系方式
Zhangyundi - yundi.xxii@outlook.com