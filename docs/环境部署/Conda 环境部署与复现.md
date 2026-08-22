# Conda 环境部署与复现（big-data-skills）

## 1. 目标

本仓库使用 conda + pip 进行 Python 环境管理，并采用：

- 全局学习环境：`big-data-skills/environment.yml`
- Demo 专用环境：`Python_Pandas/ETL_DEMO1_FULL_LOAD/environment.yml`

本文件记录环境创建、更新、迁移与复现的落地流程。

---

## 2. Conda 安装

优先使用 Miniconda。

- Windows 安装包路径（仓库内置）：`InstallPackages/Miniconda3-latest-Windows-x86_64.exe`

安装完成后如果 PowerShell 中 `conda` 不可用，执行一次：

```powershell
conda init powershell
```

然后关闭并重新打开 PowerShell。

---

## 3. 建议的 Conda 配置（统一 channel）

推荐统一使用 conda-forge，并启用 strict 优先级：

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

---

## 4. 全局环境（推荐日常学习用）

### 4.1 创建

在仓库根目录执行：

```bash
cd g:\DataSkills\big-data-skills
conda env create -f environment.yml
conda activate big-data-skills
```

### 4.2 更新（yml 修改后）

```bash
conda env update -f environment.yml --prune
```

### 4.3 删除（不常用）

```bash
conda env remove -n big-data-skills
```

---

## 5. ETL_DEMO1_FULL_LOAD 专用环境

### 5.1 创建

```bash
cd g:\DataSkills\big-data-skills
conda env create -f Python_Pandas/ETL_DEMO1_FULL_LOAD/environment.yml
conda activate big-data-skills-etl-demo1
```

### 5.2 更新（yml 修改后）

```bash
conda env update -f Python_Pandas/ETL_DEMO1_FULL_LOAD/environment.yml --prune
```

---

## 6. 可复现交付建议

### 6.1 交付 `environment.yml`

对学习仓库来说，`environment.yml` 已能满足大多数“可复现”需求。

建议：

- 新成员按 yml 创建环境
- CI 按 yml 创建环境并运行测试

### 6.2 需要更强一致性时（进阶）

当团队规模扩大或对构建一致性要求更高时，可以引入：

- `conda-lock`：生成 lock 文件锁到具体构建产物

思路：

1. 维护 `environment.yml`（声明想要什么）
2. 生成 lock（锁定装什么）
3. CI/生产优先使用 lock 安装

---

## 7. Notebook/Jupyter（可选）

如果使用 Jupyter，建议为每个 conda 环境注册 kernel，便于在 notebook 中选择正确环境。

全局环境：

```bash
conda activate big-data-skills
python -m ipykernel install --user --name big-data-skills --display-name "Python (big-data-skills)"
```

ETL 环境：

```bash
conda activate big-data-skills-etl-demo1
python -m ipykernel install --user --name big-data-skills-etl-demo1 --display-name "Python (ETL_DEMO1_FULL_LOAD)"
```

---

## 8. 常见问题

### 8.1 `conda` 命令不可用

原因通常是没有初始化 shell 或 PATH 未生效。

PowerShell：

```powershell
conda init powershell
```

重开终端后再试 `conda --version`。

### 8.2 pip 装错环境

统一使用：

```bash
python -m pip install ...
```

并确保已 `conda activate <env>`。

