# 项目更新与维护指南（PROJECT UPDATE GUIDE）

> 适用：Morningstar202604.github.io 组织下全部自建仓库（GitHub 主源 + Gitee/GitCode 镜像）。

## 1. 架构一览

| 平台 | 角色 | 说明 |
|---|---|---|
| GitHub（Morningstar202604） | **唯一代码源头** | 所有开发、CI、依赖更新、安全告警都在这里 |
| Gitee（badhope） | 镜像备份/国内展示 | 与 GitHub 同步，无独立开发流程 |
| GitCode（badhope） | 镜像备份/国内展示 | 与 GitHub 同步，无独立开发流程 |

开发只发生在 GitHub：**推 GitHub = 全平台都有**；镜像在需要发布时一次性同步（见 §5）。

## 2. 日常更新流程（开一个 PR 三步走）

```bash
# 1) 克隆并建分支
git clone git@github.com:Morningstar202604/你的项目.git
cd 你的项目 && git checkout -b feat/你的改动

# 2) 改代码、本地验证 → 提交推分支
git add -A && git commit -m "feat: 说明改动"
git push -u origin feat/你的改动

# 3) 开 PR（main 被保护，禁止直接 push，必须走 PR）
gh pr create --base main --fill
```

PR 打开后系统自动运行：
- 仓库的 **CI 必检项**（lint / 类型检查 / 单测 / 构建，各仓库按技术栈略有差异）
- Dependabot / 安全扫描等
- **全绿后**，手动点 Merge（推荐 Squash）即可合并；合并后自动删除该分支

> PR 标着 `X checks pending` → 等一会；`X checks failing` → 看具体失败 job 修掉再合。

## 3. 依赖与安全（Dependabot，全自动）

- **每周** Dependabot 自动检查全仓库依赖并开更新 PR。
- **minor/patch**（小版本、bug 修复）→ 由 `dependabot-auto-merge.yml` **自动合并**，CI 过了自己进 main，你不用管。
- **major**（大版本，如 typescript 7、vite 8）→ 自动合并会跳过，**留给你人工审**。审完点 Merge 或在 [Dependabot PR 列表](https://github.com/Morningstar202604?tab=repositories) 里逐个处理。
- **安全漏洞**：GitHub 每仓库 **Security → Dependabot alerts** 查看；高危漏洞 Dependabot 会直接开修复 PR，minor 自动合。

## 4. 已开启的保护（17 个自建仓库全部生效）

- 分支保护：main 必须走 PR、必检项通过、**禁强推、禁删分支**、合并后自动删分支
- Allow auto-merge / Delete branch on merge / Update branch
- Dependabot alerts + security updates、Secret scanning（含 push protection）
- Gitee/GitCode 镜像：main 分支保护已开（仅管理员可推/合并）

## 5. 镜像同步（Gitee / GitCode）

镜像按需一次性同步（GitHub 为主，不常需）。同步命令：

```bash
# 逐个仓库：GitHub main → Gitee/GitCode
git clone --mirror git@github.com:Morningstar202604/<repo>.git /tmp/<repo>.git
cd /tmp/<repo>.git
git push --mirror https://<gitee用户名>:<Gitee私有Token>@gitee.com/badhope/<repo>.git
git push --mirror https://badhope:<GitCode私有Token>@gitcode.com/badhope/<repo>.git
```

> Token 建议存到本地密码管理器，不要写进仓库。

## 6. 平台与仓库速查

| 仓库 | 技术栈 | 依赖更新生态 |
|---|---|---|
| AgentSeed / sandtable / medconsult / overhaul / FinHub | Python | pip |
| scholarhub | Python + React | pip + npm |
| VerdictAI | Python + React | pip + npm（前后端分目录）|
| KeBaiPay / OpenBox / campushub / fogsea-survival | JavaScript | npm |
| codecrew | Go | gomod |
| areyoudeadyet / mashang-python | Kotlin/Android | gradle |
| ScholarSeed / nebula / awesome-skillkit | 无锁文件依赖 | 仅 github-actions |

## 7. 常见问题

- **PR 合不了（BLOCKED）**：看必检项哪个红；红的是外部检查（如 AI 审查缺 Key）就把该检查从分支保护移除，或补上对应 Secret。
- **误标依赖更新大版本**：可临时在 `.github/dependabot.yml` 给某依赖加 `ignore`，如 `- dependency-name: "typescript"`。
- **改了 ci.yml 后必检项失效**：分支保护里把必检项名字改成新 job 名（Settings → Branches → Edit rule）。
- **想关闭自动合并**：删掉 `.github/workflows/dependabot-auto-merge.yml` 即可。

---

维护人：Morningstar202604　·　2026-08 建立