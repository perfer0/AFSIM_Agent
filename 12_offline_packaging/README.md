# Step 12 - Offline Packaging

这一课做离线交付包。

目标不是把所有东西都压进去，而是明确区分：

```text
代码 / 提示词 / 配置 / 报告       放进离线包
Ollama 大模型 blob               不放进离线包
AFSIM 安装目录和 mission.exe      不放进离线包
仿真 .aer/.evt/.log 输出          不放进离线包
```

## 怎么运行

```powershell
cd D:\AFsim\Agent\12_offline_packaging
python .\package_project.py build
python .\package_project.py verify
```

## 产物

```text
build/AFSIM_Agent_offline_YYYYMMDD_HHMMSS.zip
build/package_manifest.json
build/package_checksums.json
build/package_verify.json
```

压缩包里会额外写入：

```text
AFSIM_Agent/OFFLINE_RESTORE.md
```

## 成功标准

```text
package_verify.json.passed = true
压缩包里没有 ollama/models/
压缩包里没有 .aer/.evt/.log/.pyc
package_manifest.json 记录 archive_sha256
```

## 重点理解

离线项目交付要分清三类东西：

```text
项目资产：应该版本化和打包
运行时资产：需要本机安装，例如 AFSIM 和 Ollama
大文件资产：放 D:\AFsim\Agent\ollama\models，但不进 Git、不进源码包
```

这一步让项目从“能在我机器上跑”变成“有明确迁移边界”。
