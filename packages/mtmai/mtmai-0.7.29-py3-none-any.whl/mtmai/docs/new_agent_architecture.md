# mtmai新Agent架构文档

## 概述

基于autogen v0.7.2重构的mtmai Agent架构，符合最新的文档要求和设计原则。

## 设计原则

1. **统一的请求响应格式** - 所有Agent使用相同的`AgentRequest`和`AgentResponse`格式
2. **多入口支持** - Agent可从HTTP端点、消息队列、任务调度等多种入口调用
3. **简化的API端点** - 端点仅作为Agent运行的入口，不包含过多业务逻辑
4. **可扩展的注册机制** - 支持动态注册新的Agent类型
5. **基于autogen v0.7.2** - 使用最新的autogen架构和最佳实践

## 核心组件

### 1. MtBaseAgent基类

```python
from mtmai.agents._mtbase_agent import MtBaseAgent, AgentRequest, AgentResponse

class MyAgent(MtBaseAgent):
    async def execute(self, request: AgentRequest) -> AgentResponse:
        # 实现具体的Agent逻辑
        pass
```

**特性：**
- 抽象基类，定义了Agent的标准接口
- 统一的请求响应格式
- 支持autogen集成
- 可选的工具和记忆功能

### 2. 统一的数据格式

#### AgentRequest
```python
class AgentRequest(BaseModel):
    task: str                           # 任务描述
    context: Optional[Dict[str, Any]]   # 上下文信息
    config: Optional[Dict[str, Any]]    # 配置参数
```

#### AgentResponse
```python
class AgentResponse(BaseModel):
    success: bool                       # 执行是否成功
    result: Optional[str]               # 执行结果
    error: Optional[str]                # 错误信息
    metadata: Optional[Dict[str, Any]]  # 元数据
```

### 3. Agent注册机制

```python
from mtmai.api.agent_runner import register_agent

# 注册新的Agent类型
register_agent("my_agent", MyAgent, my_agent_factory)
```

## 重构的Agent实现

### 1. AssistantAgent

重构后的`AssistantAgent`：
- 继承`MtBaseAgent`基类
- 支持动态模型客户端创建
- 统一的执行接口
- 保持与原有API的兼容性

### 2. MtmaiAgent（范例）

新的范例Agent展示：
- 任务类型识别（浏览、分析、通用）
- 数据库步骤记录
- 可扩展的业务逻辑
- 工厂函数支持

## API端点

### 1. 聊天Agent端点（兼容）

- `POST /api/mtmai/chat/chat` - 兼容原有聊天API
- `WebSocket /api/mtmai/chat/ws` - WebSocket聊天支持

### 2. 新的Agent运行器端点

- `GET /api/mtmai/agents/agents` - 获取可用Agent列表
- `POST /api/mtmai/agents/run` - 运行指定类型的Agent
- `POST /api/mtmai/agents/run/{agent_type}` - 运行特定Agent（简化接口）
- `GET /api/mtmai/agents/health` - 健康检查

## 使用示例

### 1. 创建自定义Agent

```python
from mtmai.agents._mtbase_agent import MtBaseAgent, AgentRequest, AgentResponse

class CustomAgent(MtBaseAgent):
    async def execute(self, request: AgentRequest) -> AgentResponse:
        try:
            # 处理任务逻辑
            result = await self.process_task(request.task)
            
            return AgentResponse(
                success=True,
                result=result,
                metadata={"agent_name": self.name}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=str(e)
            )
```

### 2. 注册和使用Agent

```python
from mtmai.api.agent_runner import register_agent

# 注册Agent
register_agent("custom", CustomAgent)

# 通过API调用
POST /api/mtmai/agents/run
{
    "agent_type": "custom",
    "task": "执行自定义任务",
    "config": {"param": "value"}
}
```

### 3. 直接使用Agent

```python
agent = CustomAgent()
request = AgentRequest(task="测试任务")
response = await agent.execute(request)

if response.success:
    print(f"结果: {response.result}")
else:
    print(f"错误: {response.error}")
```

## 迁移指南

### 从旧架构迁移

1. **继承新基类**：将Agent类改为继承`MtBaseAgent`
2. **实现execute方法**：使用统一的`AgentRequest`和`AgentResponse`
3. **更新API调用**：使用新的端点格式
4. **注册Agent**：使用注册机制替代硬编码

### 兼容性

- 原有的聊天API保持兼容
- 逐步迁移到新架构
- 支持新旧Agent并存

## 测试

运行测试验证新架构：

```bash
uv run python -m pytest mtmai/tests/test_new_agent_architecture.py -v
```

测试覆盖：
- 基类功能
- Agent创建和执行
- 请求响应格式
- 注册机制
- 任务类型识别

## 优势

1. **标准化** - 统一的接口和数据格式
2. **可扩展** - 易于添加新的Agent类型
3. **可维护** - 清晰的架构和职责分离
4. **可测试** - 完整的测试覆盖
5. **符合文档要求** - 遵循最新的设计原则

## 下一步

1. 迁移更多现有Agent到新架构
2. 添加更多工具和记忆功能
3. 完善监控和日志
4. 扩展多入口支持（消息队列、任务调度等）
