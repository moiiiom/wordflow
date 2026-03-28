# WordFlow

英语单词记忆工具，基于你的 `data/words.csv` 词库，纯静态页面，无需构建。

## 功能

- **卡片模式**：单张卡片展示单词，点击翻转查看笔记，键盘 `←` `→` 切换，空格键翻转
- **大厅模式**：网格展示所有单词，按颜色筛选
- **颜色标记**：灰色（未标记）/ 红色（不会）/ 黄色（模糊）/ 绿色（掌握），刷新后保持
- **随机模式**：打乱卡片顺序练习

## 数据格式

`data/words.csv` 两列：`Vocabulary`（单词）和 `Notes`（笔记），支持多行、HTML 标签、emoji。

## 本地运行

需要通过 HTTP 服务器打开（不能直接双击 html 文件）：

```bash
# Python 3
python3 -m http.server 8080
# 然后访问 http://localhost:8080
```

## GitHub Pages 部署

1. 将代码 push 到 GitHub 仓库
2. 进入仓库 **Settings → Pages**
3. Source 选择 `main` 分支，目录选 `/` (root)
4. 保存后访问 `https://<your-username>.github.io/<repo-name>/`
