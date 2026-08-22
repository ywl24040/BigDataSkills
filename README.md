# BigDataSkills

#### 介绍
大数据技术栈，针对ETL开发人员的技能补充

#### 软件架构

```toml
[project]
requires-python = ">=3.12,<3.13"
```

#### 环境管理（Conda + pip）

本仓库采用“全局学习环境 + Demo 专用环境”的方式进行 Python 环境管理（更规范、可复现）。

环境文件：

- 全局环境：[environment.yml](file:///g:/DataSkills/big-data-skills/environment.yml)
- ETL_DEMO1_FULL_LOAD 专用环境：[environment.yml](file:///g:/DataSkills/big-data-skills/Python_Pandas/ETL_DEMO1_FULL_LOAD/environment.yml)

Conda 安装（Windows）：

- 本仓库提供 Miniconda 安装包：[Miniconda3-latest-Windows-x86_64.exe](file:///g:/DataSkills/big-data-skills/InstallPackages/Miniconda3-latest-Windows-x86_64.exe)
- 安装后如 PowerShell 中 `conda` 不可用，可执行一次并重开终端：

```powershell
conda init powershell
```

Conda 建议配置（可选）：

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

创建/使用全局环境（推荐日常学习用）：

```bash
conda env create -f environment.yml
conda activate big-data-skills
```

创建/使用 ETL_DEMO1_FULL_LOAD 专用环境（跑 Demo 用）：

```bash
conda env create -f Python_Pandas/ETL_DEMO1_FULL_LOAD/environment.yml
conda activate big-data-skills-etl-demo1
```

更新环境（environment.yml 修改后）：

```bash
conda env update -f environment.yml --prune
```

#### 公共包（bds_common）

本仓库将“数据库配置加载 + MySQL 连接创建”等公共能力封装为 Python 包 `bds_common`，以便所有 Demo 像使用第三方库一样直接导入。

源码位置：

- [common/python](file:///g:/DataSkills/big-data-skills/common/python)

开发环境安装（推荐，可编辑安装）：

```bash
conda activate big-data-skills
python -m pip install -e common/python
```

Demo 中使用示例：

```python
from bds_common import DB_CONFIG, create_mysql_engine

engine = create_mysql_engine(config=DB_CONFIG)
```

部署/打包说明：

- [python_package_deployment_bds_common.md](file:///g:/DataSkills/big-data-skills/GuideLine/DeploymentManagement/python_package_deployment_bds_common.md)

ETL Demo 位置：

- 代码目录：[ETL_DEMO1_FULL_LOAD/Code/Python](file:///g:/DataSkills/big-data-skills/Python_Pandas/ETL_DEMO1_FULL_LOAD/Code/Python)

参考文档：

- [python_conda_pip_enterprise_env_management.md](file:///g:/DataSkills/big-data-skills/GuideLine/EnvConfigurationManagement/python_conda_pip_enterprise_env_management.md)

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
