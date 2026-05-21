# 基于 PRD 的自动化测试与缺陷生成插件（Demo）

## 项目简介

本项目实现了一个简化版自动化测试插件原型。

插件以产品需求文档（PRD）为输入，自动完成：

- PRD 规则提取
- 需求分析
- 测试用例生成
- 自动化测试执行
- 缺陷检测
- 测试报告生成

当前 Demo 以 Flask 登录注册系统作为被测系统（SUT）。

系统中故意保留一个后端缺陷，用于验证插件能否自动发现需求与实现不一致的问题。

---

## 工作流程

```text
PRD 文档
    ↓
规则提取
    ↓
需求分析
    ↓
测试用例设计
    ↓
自动化执行
    ↓
缺陷检测
    ↓
测试报告生成
当前实现模块
注册模块

当前实现的验证规则：

用户名不能为空
用户名长度 > 6
密码不能为空
密码长度 > 8
邮箱格式校验
确认密码一致
重复用户名检测
登录模块

当前测试场景：

正确登录
密码错误登录
空输入验证
用户不存在场景
预设缺陷（Intentional Bug）

PRD 要求：

用户名长度必须大于 6

但后端实现中故意未添加用户名长度校验：

# 故意保留缺陷
# 未实现用户名长度验证

例如：

{
   "username":"abc",
   "password":"123456789"
}

理论结果：

注册失败

实际结果：

注册成功

插件会自动检测到该异常，并生成缺陷。

项目结构
project/

│── demo_workflow.py
│── README.md
│── PRD.md

├── backend
│    └── app.py

└── output
     │── rules.json
     │── requirements.json
     │── test_cases.json
     │── bugs.json
     │── report.json
     └── test_report.md
自动生成文件说明
1. rules.json

保存 PRD 中提取出的规则。

示例：

{
   "rule_id":"RULE_001",
   "field":"username",
   "condition":"length_greater_than",
   "value":6
}
2. requirements.json

保存需求分析结果。

示例：

{
   "requirement_id":"REQ_001",
   "module":"register",
   "field":"username",
   "type":"validation"
}
3. test_cases.json

自动生成测试用例。

示例：

{
   "case_id":"TC_REG_001",
   "description":"用户名长度不足测试"
}
4. bugs.json

自动生成缺陷。

示例：

{
   "bug_id":"BUG_TC_REG_001",
   "severity":"HIGH",
   "priority":"P1",
   "status":"OPEN"
}
5. test_report.md

自动生成测试报告。

报告包含：

测试总数
通过 / 失败统计
缺陷汇总
执行结果
当前运行结果

当前 Demo 执行结果：

总测试用例：8

通过：6

失败：2

自动发现缺陷：2

发现问题包括：

用户名长度未校验
PRD 与实现不一致
技术栈

后端：

Python 3
Flask
Flask-CORS

测试：

Flask Test Client
JSON
正则规则提取

输出：

Markdown 报告
JSON 文件
运行方式

安装依赖：

pip install flask flask-cors

运行项目：

python demo_workflow.py

运行结束后生成：

output/

rules.json
requirements.json
test_cases.json
bugs.json
report.json
test_report.md
后续规划
缺陷系统增强

计划增加：

自动 Bug ID
严重等级划分
优先级划分
缺陷模板
测试能力扩展

登录模块新增：

空用户名
空密码
非法用户
SQL 注入测试
边界测试
特殊字符测试
可视化面板

后续计划：

展示：

测试通过率
失败率
Bug 数量
趋势图
Agent 化能力

最终目标：

PRD
 ↓
需求分析 Agent
 ↓
测试设计 Agent
 ↓
执行 Agent
 ↓
缺陷生成 Agent
 ↓
报告 Agent

实现完整自动测试插件流程。

当前完成状态

已完成流程：

PRD → 需求分析 → 测试设计 → 自动执行 → 缺陷生成 → 测试报告

当前版本为自动化测试插件 MVP 原型。
