# CFU 持久执行探针（PROTOTYPE）

问题：固定焦点提议后，进程退出／重启、同一回应重送、产物写入后崩溃，是否仍能恢复同一决定并只交接对应版本？关联 [运行原型票](../../issues/09-cfu-runtime-prototype.md)。

这是一次性运行实验，不是 CFU 生成器或生产服务。材料和模型输出固定，使用八年级 CCSS 8.F.B.4；不证明教学质量，也不读取 IM。程序事件标为 `fixture`；真实参与只从实际回应取得，参与者为原型评阅人，不冒称合作学校教师。

验证范围：SQLite checkpointer 的跨进程恢复；请求／回应的应用记录；固定模型通过 LangChain Agent 的工具往返；两份材料的实际版本检查；注入进程退出；已有有效焦点；取消和旧版本保护。Agent Server 开发运行另记结果，不能外推 PostgreSQL／生产恢复或 LangSmith 云服务。

运行：

```sh
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.prototype.lock
.venv/bin/python exercise.prototype.py
```

在本目录运行。每轮探针新建 `runs/` 子目录，保存命令、进程身份、状态和判据；`PROTOTYPE-checkpoints.sqlite` 与 `PROTOTYPE-business.sqlite` 均为独立临时数据库，不能连接外部真实业务库。每个 CLI 命令是新进程，等待后不保留模型计算。

实际输出以 `results.json` 和后续运行记录为准。原型规则、调用方式及未覆盖范围随验证结果补充；不要将模拟通过值当真人教学接受。

## 本轮结果

见 [实测结论](../../assets/cfu-durable-prototype-results.md)。13 项固定事件故障探针通过；另有一次真实原型回应，经保存后硬退出再恢复；Agent Server dev 的实际服务重启／恢复已走通。LangSmith SDK 只对本地 HTTP 记录器验证发送、字段处理和 503 故障，不是云服务接入。

- [最新故障记录](runs/20260915T032753757782Z-faults/results.json)
- [真实回应恢复](runs/real-review/real-recovery.json)
- [服务接口与重启](server-probe.json)
- [LangSmith SDK 本地发送](runs/20260915T032913870963Z-trace/sdk-transport.json)

本次逐命令进程探针保留原始状态，不再创建新的模拟 UI。`runtime_probe_complete` 是运行样本完成，不是教学质量通过；`verify` 只验证成对材料和快照，完整教学检查没有实现。

服务复现使用 `.venv/bin/langgraph dev --host 127.0.0.1 --port 62915 --no-browser --no-reload`，再运行 `server_exercise.prototype.py start`；停止并重启服务后运行 `server_exercise.prototype.py resume`。已有 `server-probe.json` 会阻止覆盖，须在另一个原型副本运行，不能删除旧记录后冒充同一轮。LangSmith SDK 的独立探针用 `.venv/bin/python trace_exercise.prototype.py`，只连接自动分配的本地记录器端口。
