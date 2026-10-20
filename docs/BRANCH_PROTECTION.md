# 分支保护：让锁定内容物理不可回滚

`lock.py` 提供的是「可检测的防篡改」（哈希 + tag）。要让内容「物理上不可回滚/改写」，
必须叠加 git 分支保护——否则任何人（或刷新工作流）仍可 force-push 覆盖。

## GitHub（gh_badhope / gh_morningstar / gh_x33834）

仓库 Settings → Branches → 给 `main` 添加规则：

- [x] Require a pull request before merging
- [x] Require approvals = 1（或更多）
- [x] **Do not allow bypassing the above settings**
- [x] **Require linear history**（禁止强制改写已合入历史）
- [x] Do not allow force pushes（关键：关掉 force-push）
- [x] Do not allow deletions of this branch
- [ ] 允许刷新机器人自批自合（务必关掉，否则自动合并等于无保护）

效果：刷新 PR 必须人工审核；`lock-*` tag 指向的提交落在受保护历史上，无法被改写或删除。
`refresh.yml` 的 `mirror` 作业改用 **oauth2 token** 推送（普通 push，非 force），受保护分支会拒绝
未审核的强制推送，因此 GitCode/Gitee 镜像也会保持与已审核的 main 一致。

## GitCode / Gitee

两平台原生分支保护较弱，依赖「镜像来自受保护 GitHub main」这一事实：只有审核过的 main
才会被 `mirror` 作业推过去。请勿在 GitCode/Gitee 侧手动改 main，也不要把它们的 token 用于
任何自动回写脚本。

## 验证

```bash
# 本地：篡改后能否被 lock.py 发现
python3 scripts/lock.py --verify
# 期望：verify: DRIFT detected ... MODIFIED <file>

# 远端：尝试 force-push 应被拒绝
git push --force origin main   # 期望：remote rejected (protected branch)
```
