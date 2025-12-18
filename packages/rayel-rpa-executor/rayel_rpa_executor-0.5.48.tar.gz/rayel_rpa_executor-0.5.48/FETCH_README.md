同步上游仓库（upstream）到私有仓库指引

一、一次性设置

1) 添加原作者仓库为 upstream（只需一次）：

```bash
git remote -v
git remote add upstream <原作者仓库URL>   
git remote set-url upstream <原作者仓库URL> # 若已存在用 set-url 更新
```

二、获取与合并更新

1) 获取上游最新提交：

```bash
git fetch upstream
```

2) 合并到你的主分支（保持完整历史，推荐已推送分支用 merge）：

```bash
git checkout main   # 或你的默认分支
git merge upstream/main
```

可选：若希望线性历史，用 rebase（会改写历史，谨慎）：

```bash
git checkout main
git rebase upstream/main
```

3) 解决冲突（如有）：

```bash
git status
# 编辑冲突文件 → 解决后
git add <文件...>
git commit              # merge 流程
# 或
git rebase --continue   # rebase 流程
```

4) 推送到你的私有仓库：

```bash
git push origin main
# 若使用了 rebase 且已推送过：
# git push origin main --force-with-lease
```

三、VSCode 插件（界面化操作）

- GitLens（推荐，ID: eamodio.gitlens）
  - 左侧 GitLens 视图 → Repositories → Remotes
  - 右键 Remotes → Add Remote，名称填 upstream，URL 填原作者地址
  - 在 upstream/main 上右键：Fetch → Merge into current branch 或 Rebase current branch onto
  - 合并后在当前分支右键 Push 推送到 origin

- Git Graph（ID: mhutchie.git-graph）
  - 打开 Git Graph 视图，右键分支进行 Merge/Rebase、Push、查看历史等

四、自动化脚本（可选）

```bash
#!/bin/bash
# sync-upstream.sh
set -e
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

五、最佳实践

- 已共享的分支用 merge 更安全；必须强推时用 --force-with-lease
- 先在临时同步分支验证合并，再合并回 main，降低风险
- 按周或按迭代定期同步，避免一次性冲突过大


