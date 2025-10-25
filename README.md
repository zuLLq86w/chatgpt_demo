### 1.项目结构
``` bash
backend/
├── app/
│   ├── api/                         # 路由层（仅负责 HTTP 请求的入口）
│   ├── core/                        # 核心配置 & 中间件
│   ├── models/                      # ORM 模型（数据库实体）
│   ├── repository/                  # 仓储层（封装SQL操作逻辑）
│   ├── services/                    # 业务逻辑层（调用repository + 外部API）
│   ├── schemas/                     # 数据验证层（Pydantic模型）
│   ├── tools/                       # 工具层（第三方集成）
│   └── __init__.py
├── alembic/                         # 数据库迁移文件夹
├── main.py                          # 项目入口，启动FastAPI
├── .env                             # 环境变量配置文件
└── README.md
```

### 2.技术栈与版本

- python: 3.12
- web框架: fastapi 0.120.0(异步，内建OpenAPI)
- ORM: sqlalchemy 2.0(异步AsyncSession)
- DB: mysql(异步 aiomysql)
- 请求校验/序列化: pydantic 2.12

### 3.API端点列表
```
http://localhost:8000/docs
```

### 4.数据库Schema设计说明
主要表

- users: 用户
- tags: 标签
- conversations: 会话
- conversation_tal_rel: 会话与标签关系
- messages: 消息记录
- groups: 群组
- group_members: 群组成员
- group_robots: 机器人
- group_robot_rel: 群组与机器人关系

### 5.本地启动与运行步骤

1. 创建虚拟环境(python 3.12)
```shell
# 推荐使用uv
uv venv  # 创建虚拟环境
uv sync --frozen  # 安装依赖
```
2. 配置.env
3. 数据库迁移
```shell
alembic upgrade head 
```
4. 启动服务
```shell
python main.py 
```
5. 打开文档
http://127.0.0.1:8000/docs

6. 部署

### 6.设计说明

1. 技术选型
- FastAPI: 支持异步，能够自动生成OpenAPI，开发效率高，性能高。
- SQlAlchemy: AsyncSession + Mysql(aiomysql) 支持复杂查询，同时支持异步操作，性能较高，容易部署。
- Pydantic：能够校验请求，序列化响应，开发效率高
- PyJWT：跨语言/跨服务的标准认证方式，简单且安全

2. 对话标签
- 通过conversation_tsg_rel中间表来存储会话与标签的关系，允许每个会话有多个标签，支持按多个标签筛选，

3. AI API调用健壮性
- 始终保存用户消息
- 封装AI调用工具，增加重试策略
- 可以使用httpx替换openai sdk，实现异步请求，提高程序的并发量
- 单个AI key可以使用Semaphore限制并发量
- AI调用历史入库，方便后续排查

4. 群组对话
- group表配置机器人回复策略，所有，随机，关键字
- http方式实现群组消息：用户发送消息 -> 后端调用AI API -> 返回前端, 不会触发循环
- 防循环策略：消息增加flag, 当flag为robot时忽略；同一次用户消息只允许最多n个机器人回复；限制机器人回复时间，只有当机器人最后一次回复时间超过N秒后才允许回复
- 当机器人回复消息为空时，回复一条固定模版