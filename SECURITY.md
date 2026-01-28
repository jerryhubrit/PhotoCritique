# API Key 安全配置指南 🔐

## ✅ 已完成的安全配置

### 1. 环境变量文件

**`.env`** - 包含真实的API Key（已被Git忽略）
```bash
INTERNLM_API_KEY=your_actual_api_key_here
```

**`.env.example`** - 配置模板（会上传到Git）
```bash
INTERNLM_API_KEY=your_api_key_here
```

### 2. Git 忽略配置

**`.gitignore`** 文件已添加以下规则：
```
# 环境变量文件（包含真实的API Key）
.env

# 测试和临时文件
test_*.html
*_report.html
```

### 3. 代码修改

#### batch_analyzer.py
```python
# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 从 .env 文件加载环境变量
except ImportError:
    print("⚠️  提示: 未安装 python-dotenv，将从系统环境变量读取配置")
```

#### emotion_analyzer.py
```python
# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

API Key 读取逻辑（已有）：
```python
self.api_key = api_key or os.getenv("INTERNLM_API_KEY")
```

### 4. 依赖包安装

```bash
pip install python-dotenv --user
```

## 📋 使用流程

### 首次配置（新用户）

1. **克隆项目后**
   ```bash
   git clone <your-repo>
   cd photo-ai
   ```

2. **复制配置模板**
   ```bash
   cp .env.example .env
   ```

3. **编辑 .env 文件，填入真实的API Key**
   ```bash
   vim .env  # 或使用其他编辑器
   ```

4. **安装依赖**
   ```bash
   pip install python-dotenv
   ```

5. **开始使用**
   ```bash
   python3 batch_analyzer.py your_photo.jpg
   ```

### Git 提交流程

```bash
# 查看状态 - .env 不会出现在列表中
git status

# 添加文件
git add .gitignore .env.example README.md batch_analyzer.py

# 提交
git commit -m "feat: 添加环境变量配置和API Key保护"

# 推送
git push
```

## 🔍 验证安全性

### 检查 .env 是否被忽略

```bash
# 方法1：查看 git status，.env 不应出现
git status

# 方法2：使用 git check-ignore
git check-ignore -v .env
# 输出：.gitignore:2:.env    .env
```

### 确认文件存在

```bash
ls -la | grep .env
# 应显示：
# .env          (真实密钥，被Git忽略)
# .env.example  (模板，会上传到Git)
```

## ⚠️ 安全注意事项

### ❌ 不要做的事

1. **不要**直接在代码中硬编码API Key
2. **不要**将 `.env` 文件添加到Git
3. **不要**在公开的文档中暴露真实密钥
4. **不要**将密钥截图分享

### ✅ 应该做的事

1. **始终**使用环境变量存储密钥
2. **定期**更换API Key
3. **仅在**`.env.example`中提供模板
4. **确保**`.gitignore`包含`.env`
5. **检查**提交历史中是否有密钥泄露

## 🆘 密钥泄露处理

如果不小心将 `.env` 提交到了Git：

1. **立即更换API Key**
   - 登录 InternLM 平台
   - 撤销旧密钥
   - 生成新密钥

2. **从Git历史中删除**
   ```bash
   # 方法1: 使用 git filter-branch（慎用）
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   # 方法2: 使用 BFG Repo-Cleaner（推荐）
   bfg --delete-files .env
   ```

3. **强制推送**
   ```bash
   git push --force --all
   ```

## 📚 相关文档

- [README.md](README.md) - 项目使用说明
- [.env.example](.env.example) - 配置模板
- [.gitignore](.gitignore) - Git忽略规则

## ✅ 检查清单

- [x] 创建 `.env` 文件存储真实密钥
- [x] 创建 `.env.example` 模板文件
- [x] 添加 `.gitignore` 忽略 `.env`
- [x] 代码中使用 `python-dotenv` 加载环境变量
- [x] 验证 `.env` 不会被Git追踪
- [x] 安装 `python-dotenv` 依赖
- [x] 测试环境变量正常读取
- [x] 创建使用文档

---

**当前状态**: ✅ 所有安全配置已完成，API Key 已受保护！
