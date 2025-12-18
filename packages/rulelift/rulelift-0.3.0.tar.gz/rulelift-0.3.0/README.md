# rulelift

一个用于信用风险管理中规则有效性分析的Python工具包。

## 功能介绍

rulelift可以帮助您分析信用风险规则的有效性，包括：

- 基于用户评级坏账率（USER_LEVEL_BADRATE）的预估指标
- 基于实际逾期情况（USER_TARGET）的实际指标
- 核心指标包括：命中率、逾期率、召回率、精确率、lift值等
- 支持自定义字段映射
- 输出结构化的分析结果

## 安装方法

```bash
pip install rulelift
```

## 快速开始

### 1. 加载示例数据

```python
from rulelift import load_example_data

# 加载示例数据
df = load_example_data()

# 查看数据结构
df.head()
```

### 2. 分析规则效度

```python
from rulelift import analyze_rules

# 分析规则效度
result = analyze_rules(df)

# 查看分析结果
print(result.head())

# 按lift值排序
result_sorted = result.sort_values(by='actual_lift', ascending=False)
print(result_sorted.head())
```

## API文档

### analyze_rules

```python
def analyze_rules(rule_score, rule_col='RULE', user_id_col='USER_ID', 
                 user_level_badrate_col='USER_LEVEL_BADRATE', user_target_col='USER_TARGET')
```

#### 参数

- `rule_score`: DataFrame，规则拦截客户信息
- `rule_col`: str，规则名字段名，默认值为'RULE'
- `user_id_col`: str，用户编号字段名，默认值为'USER_ID'
- `user_level_badrate_col`: str，用户评级坏账率字段名，默认值为'USER_LEVEL_BADRATE'
- `user_target_col`: str，用户实际逾期字段名，默认值为'USER_TARGET'

#### 返回值

- DataFrame，包含所有规则的评估指标，包括：
  - `rule`: 规则名称
  - `hit_rate_pred`: 基于评级坏账率的预估命中率
  - `estimated_badrate_pred`: 基于评级坏账率的预估逾期率
  - `estimated_recall_pred`: 基于评级坏账率的预估召回率
  - `estimated_precision_pred`: 基于评级坏账率的预估精确率
  - `estimated_lift_pred`: 基于评级坏账率的预估lift值
  - `hit_rate`: 基于实际逾期的命中率
  - `actual_badrate`: 基于实际逾期的实际逾期率
  - `actual_recall`: 基于实际逾期的实际召回率
  - `actual_precision`: 基于实际逾期的实际精确率
  - `actual_lift`: 基于实际逾期的实际lift值

### load_example_data

```python
def load_example_data(file_path='./data/hit_rule_info.csv')
```

#### 参数

- `file_path`: str，示例数据文件路径，默认值为'./data/hit_rule_info.csv'

#### 返回值

- DataFrame，示例数据

## 示例数据结构

示例数据包含以下字段：

| 字段名 | 描述 |
| ---- | ---- |
| RULE | 规则名称 |
| USER_ID | 用户编号 |
| HIT_DATE | 命中规则日期 |
| USER_LEVEL | 用户评级 |
| USER_LEVEL_BADRATE | 用户评级对应的坏账率 |
| USER_TARGET | 用户是否逾期（1=逾期，0=未逾期） |

## 指标说明

### 命中率

- 定义：命中规则的样本数 / 总样本数
- 意义：规则覆盖的样本比例

### 逾期率

- 定义：逾期样本数 / 总样本数
- 意义：样本的整体逾期情况

### 召回率

- 定义：命中规则的逾期样本数 / 总逾期样本数
- 意义：规则能够识别出的逾期样本比例

### 精确率

- 定义：命中规则的逾期样本数 / 命中规则的样本数
- 意义：规则命中的样本中实际逾期的比例

### Lift值

- 定义：规则命中样本的逾期率 / 总样本的逾期率
- 意义：规则的有效性提升倍数，值越大说明规则越有效

## 许可证

MIT License

## 作者

Author Name <author@example.com>
