# 实现记录

- 001：在 Docker tmpfs 输入区使用 docker cp 被只读根限制阻止。发生在 codex exec 之前，没有模型调用和答案。保留该目录及运行器副本。
- 改为 docker exec 经 stdin 写入精确白名单文件，仍无宿主目录挂载。
- 002：首次 codex exec，缺少基础 CA 信任库，TLS UnknownIssuer，未获得模型作答。控制端只终止该容器内 codex PID，记录 operator_stop.txt；CLI 返回码为 0 但没有 turn.completed，正确标记 runtime_error，不标成功。
- 从已有 CLI 镜像复制 CA 证书到干净镜像，仍校验证书。证书连通性探针返回 TLS verified / HTTP 403（首页防护响应，不视为模型 API 授权证明）。未跳过 TLS、未安装包、未更换模型。
- 003：仅一次修复后的追加模型调用。所有评分测试在调用前执行，score.py 从首次测试至本次评分保持不变。
- 003 运行期间改善了未来运行器的超时清理：先终止自己的 codex 子进程，以便活容器中仍可取回日志；只在无法退出时停止该容器。排除 error 类型 item 作为实质进展。此改动不影响已经启动的 003 进程、求解输入或评分器。003/implementation/run.py 留存本次实际运行的版本，根目录 run.py 是后续复跑版本。
- 新增 verify_run.py 为控制端离线核验和原始工具事件提取入口，不给求解者传递任何信息。
