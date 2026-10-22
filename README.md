# clash-config

OpenClash 分流配置，自动同步 [usbog232/clashmetadingyue](https://github.com/usbog232/clashmetadingyue) 的 `metafenliu.ini`，并叠加本仓库 `overrides.ini` 里的个人改动。

## OpenClash 订阅地址

在 **OpenClash → 订阅转换 → 订阅转换模板 = 自定义模板 → 自定义模板地址** 填：

```
https://cdn.jsdelivr.net/gh/leoz26/clash-config@main/metafenliu.ini
```

备用地址（jsDelivr 抽风时用）：

```
https://raw.githubusercontent.com/leoz26/clash-config/main/metafenliu.ini
```

> 上游更新后 jsDelivr 最多缓存 12 小时。急着生效就访问一次
> `https://purge.jsdelivr.net/gh/leoz26/clash-config@main/metafenliu.ini` 清缓存，
> 然后在 OpenClash 里重新「更新配置」。

## 文件说明

| 文件 | 作用 | 谁能改 |
|---|---|---|
| `metafenliu.ini` | **成品**，OpenClash 订阅的就是它 | 自动生成，别手改 |
| `overrides.ini` | 你的个性化改动 | 你（GitHub 网页上直接改） |
| `upstream.ini` | 上游最新原版，用来看上游改了什么 | 自动下载 |
| `apply_overrides.py` | 把改动打到上游原版上的脚本 | 一般不碰 |
| `sync.sh` | 本地一键同步（可选） | — |
| `.github/workflows/sync-upstream.yml` | 每周自动同步 | 一般不碰 |

## 怎么改自己的配置

1. 在 GitHub 网页上编辑 `overrides.ini`，把示例行行首的 `;` 去掉，或照格式写新行
2. 提交 —— push 上去会**自动**重新生成 `metafenliu.ini`（几秒后刷新页面就能看到）
3. 也可以去 **Actions → Sync upstream → Run workflow** 手动触发

支持 6 种写法（关键字是包含匹配，不用写整行）：

```
set <关键字> => <新的整行>     把「包含关键字」的整行替换掉
sub <关键字> => <新文本>       在「包含关键字」的行里，把关键字换成新文本
drop <关键字>                  删除所有包含关键字的行
append <新的整行>              文件末尾追加一行
after <关键字> => <新的整行>   在最后一个包含关键字的行之后插入
before <关键字> => <新的整行>  在第一个包含关键字的行之前插入
```

## 自动同步

每周一北京时间 08:00 自动跑：下载上游最新 `metafenliu.ini` → 应用 `overrides.ini` → 提交推送。
本地电脑开不开机都无所谓，全程在 GitHub 上跑。

**如果某条改动没生效**（上游把那行改了或删了），Actions 会显示红色失败并说明原因，
但成品仍然会照常推送更新——不会因为你某条改动失效就卡住不更新。看到红色就去
`overrides.ini` 里把对应关键字改成新写法。

## 注意

- 本仓库是**公开**的，里面只有自动生成的配置和同步脚本，没有任何 token、密码或私人订阅链接。
- 上游仓库**没有 LICENSE**（默认保留所有权利），本仓库仅作个人自用，请勿拿去二次分发或商用。
