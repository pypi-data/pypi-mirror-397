# VAD数据处理工具

这个工具包用于将VAD（Voice Activity Detection）分析结果从timestamps.json文件写入到数据库中。

## 功能特性

- ✅ 自动读取timestamps.json文件
- ✅ 验证数据格式完整性
- ✅ 将VAD分析结果写入audio_tasks表
- ✅ 支持更新segments表的音频特征
- ✅ 支持单文件和批量处理
- ✅ 完整的错误处理和日志记录
- ✅ 事务安全的数据库操作

## 文件结构

```
utils/
├── __init__.py                 # 包初始化文件
├── db_connection.py           # 数据库连接工具
├── vad_data_processor.py      # VAD数据处理核心
├── example_usage.py           # 使用示例
└── README.md                  # 本文档
```

## 数据库字段映射

### audio_tasks表字段

| JSON路径 | 数据库字段 | 说明 |
|---------|-----------|------|
| `performance.total_processing_time` | `vad_total_processing_time` | VAD总处理时间(秒) |
| `performance.audio_loading_time` | `vad_audio_loading_time` | 音频加载时间(秒) |
| `performance.stage1_vad_timestamps_time` | `vad_stage1_time` | 第一阶段处理时间(秒) |
| `performance.stage2_feature_extraction_time` | `vad_stage2_time` | 第二阶段特征提取时间(秒) |
| `performance.speed_ratio` | `vad_speed_ratio` | 处理速度比率 |
| `metadata.run_id` | `vad_run_id` | VAD运行ID |
| `metadata.source_file` | `vad_source_file_path` | 源文件路径 |
| `summary.total_speech_duration` | `vad_total_speech_duration` | 总语音时长(秒) |
| `summary.num_segments` | `vad_segment_count` | 分段数量 |
| `summary.overall_speech_ratio` | `vad_speech_ratio` | 语音比例 |
| `metadata.processing_date` | `vad_completed_at` | VAD完成时间 |
| `metadata.parameters` | `vad_current_params` | VAD参数(JSON) |
| 计算得出 | `vad_avg_segment_duration` | 平均分段时长 |
| 计算得出 | `vad_avg_speech_confidence` | 平均语音置信度 |
| 计算得出 | `vad_avg_rms` | 平均均方根值 |
| 计算得出 | `vad_avg_peak_amplitude` | 平均峰值幅度 |

### segments表字段

| JSON路径 | 数据库字段 | 说明 |
|---------|-----------|------|
| `segments[i].speech_confidence` | `speech_confidence` | 语音置信度 |
| `segments[i].rms` | `rms` | 均方根值 |
| `segments[i].peak_amplitude` | `peak_amplitude` | 峰值幅度 |
| `segments[i].file_path` | `vad_segment_file_path` | 分段文件路径 |

## 使用方法

### 1. 环境准备

确保安装了必要的依赖：

```bash
pip install psycopg2-binary
```

### 2. 数据库连接配置

工具会自动从以下位置获取数据库连接信息（按优先级）：

1. 环境变量 `DATABASE_URL`
2. 项目根目录的 `.kysely-codegenrc.json` 文件
3. 项目根目录的 `.env` 文件

### 3. 基本使用

#### 处理单个文件

```python
from vad_data_processor import process_single_timestamps_file

# 处理单个timestamps.json文件
success = process_single_timestamps_file(
    timestamps_file_path="/path/to/timestamps.json",
    task_id="your-task-id"
)

if success:
    print("✅ VAD数据处理成功")
else:
    print("❌ VAD数据处理失败")
```

#### 批量处理

```python
from vad_data_processor import process_batch_timestamps_files

# 批量处理目录下的所有timestamps.json文件
results = process_batch_timestamps_files(
    timestamps_dir="/path/to/vad/output/directory"
)

# 查看处理结果
for run_id, success in results.items():
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{run_id}: {status}")
```

#### 使用自定义映射

```python
# 如果run_id和task_id不同，可以提供映射
task_mapping = {
    "run_id_1": "task_id_1",
    "run_id_2": "task_id_2",
    # ...
}

results = process_batch_timestamps_files(
    timestamps_dir="/path/to/vad/output/directory",
    task_mapping=task_mapping
)
```

### 4. 高级用法

```python
from vad_data_processor import VADDataProcessor

# 使用上下文管理器确保数据库连接正确关闭
with VADDataProcessor() as processor:
    # 处理单个文件
    success = processor.process_timestamps_file(
        "/path/to/timestamps.json", 
        "task-id"
    )
    
    # 批量处理
    results = processor.process_batch_timestamps(
        "/path/to/vad/output/directory"
    )
```

### 5. 命令行使用

```bash
# 处理单个文件
cd scripts/python/vad/utils
python vad_data_processor.py /path/to/timestamps.json task-id

# 批量处理
python vad_data_processor.py --batch /path/to/vad/output/directory
```

## 示例

### 运行示例代码

```bash
cd scripts/python/vad/utils
python example_usage.py
```

示例代码包含：
- 数据库连接测试
- 数据库状态检查
- 单文件处理示例
- 批量处理示例
- 自定义映射示例
- 高级用法示例

## 数据验证

工具会自动验证以下内容：

1. **文件格式验证**：确保timestamps.json包含所有必需的字段
2. **任务存在性检查**：验证task_id在数据库中存在
3. **数据类型验证**：确保数据类型符合数据库schema
4. **事务完整性**：使用数据库事务确保数据一致性

## 错误处理

- 所有数据库操作都包装在事务中，失败时自动回滚
- 详细的日志记录，便于问题诊断
- 优雅的错误处理，不会中断批量处理流程

## 日志记录

工具使用Python标准logging模块，日志级别为INFO。主要日志内容：

- 数据库连接状态
- 文件处理进度
- 数据验证结果
- 事务执行状态
- 错误信息

## 性能考虑

- 使用连接池管理数据库连接
- 批量操作使用事务减少数据库往返
- 支持上下文管理器确保资源正确释放

## 注意事项

1. **任务必须存在**：在处理VAD数据之前，对应的task_id必须已在audio_tasks表中存在
2. **字段可空性**：所有VAD相关字段都是可空的，适合后处理场景
3. **segments更新**：只有当任务有关联的subtitle_id时，才会更新segments表
4. **数据覆盖**：重复处理同一个任务会覆盖之前的VAD数据

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查DATABASE_URL环境变量
   - 确认.kysely-codegenrc.json文件存在且格式正确
   - 验证数据库服务是否可访问

2. **任务不存在错误**
   - 确认task_id在audio_tasks表中存在
   - 检查task_id格式是否正确

3. **文件格式错误**
   - 确认timestamps.json文件格式完整
   - 检查文件是否损坏或不完整

4. **权限问题**
   - 确认数据库用户有UPDATE权限
   - 检查文件读取权限

### 调试技巧

1. 启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. 测试数据库连接：
```python
from db_connection import test_database_connection
test_database_connection()
```

3. 验证文件格式：
```python
import json
with open('timestamps.json') as f:
    data = json.load(f)
    print(data.keys())  # 检查顶级键
```

## 集成到现有流程

这个工具设计为独立运行，不侵入现有的VAD处理流程。建议的集成方式：

1. **VAD处理完成后调用**：在VAD分析生成timestamps.json后调用此工具
2. **定时批量处理**：设置定时任务批量处理新生成的timestamps文件
3. **API集成**：将工具封装为API端点，供其他服务调用

## 未来扩展

- 支持更多数据格式
- 添加数据质量检查
- 支持增量更新
- 添加性能监控
- 支持数据导出功能
