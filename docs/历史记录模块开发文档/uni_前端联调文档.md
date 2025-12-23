# 历史记录模块前端联调文档

## 一、接口对接说明

### 1.1 查询对话历史记录

**后端接口:**
```
GET /api/v1/history/conversations
参数: session_id(可选), page(可选), page_size(可选)
认证: Bearer Token
```

**前端调用:**
```javascript
// 文件: utils/http.js
http.getConversations({
  page: 1,
  page_size: 20,
  session_id: 'xxx' // 可选
})
```

**前端页面:**
- 文件: `pages/history/history.vue`
- 功能: 列表展示历史记录，支持分页

### 1.2 搜索历史记录

**后端接口:**
```
GET /api/v1/history/search
参数: keyword(必填), page(可选), page_size(可选)
认证: Bearer Token
```

**前端调用:**
```javascript
// 文件: utils/http.js
http.searchHistory({
  keyword: '旅行',
  page: 1,
  page_size: 20
})
```

**前端页面:**
- 文件: `pages/history/history.vue`
- 功能: 搜索框输入关键词，显示匹配结果

## 二、数据格式

### 2.1 响应格式

后端返回统一格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "session_id": "uuid-string",
        "message": "用户消息",
        "response": "助手回复",
        "timestamp": "2026-01-01T10:00:00Z"
      }
    ]
  },
  "error": null
}
```

### 2.2 前端处理

前端在 `utils/http.js` 的响应拦截器中已处理：
- `code === 200` 时返回完整响应对象
- 前端页面从 `response.data` 中获取数据

## 三、页面功能

### 3.1 历史记录列表页

**文件:** `pages/history/history.vue`

**功能:**
1. ✅ 显示历史记录列表
2. ✅ 搜索功能（关键词搜索）
3. ✅ 分页功能
4. ✅ 时间格式化显示
5. ✅ 空状态提示
6. ✅ 加载状态提示

**页面路径:**
- 通过底部TabBar的"历史"标签访问
- 路由: `/pages/history/history`

## 四、修改的文件

### 4.1 后端接口封装

**文件:** `spark-uniapp/utils/http.js`

**修改内容:**
- 修复 `getConversations` 方法，使用正确的URL路径 `/api/v1/history/conversations`
- 修复 `searchHistory` 方法，使用正确的URL路径 `/api/v1/history/search`
- 修复参数传递方式，使用URL查询参数
- 修复响应拦截器，正确处理后端返回的 `{code, message, data}` 格式

### 4.2 历史记录页面

**文件:** `spark-uniapp/pages/history/history.vue`

**实现内容:**
- 历史记录列表展示
- 搜索功能
- 分页功能
- 时间格式化
- 响应式布局

## 五、测试要点

### 5.1 功能测试

1. **列表加载**
   - 打开历史记录页面，应该能正常加载历史记录列表
   - 检查分页是否正常工作

2. **搜索功能**
   - 输入关键词，点击搜索按钮
   - 验证搜索结果是否正确
   - 测试取消搜索功能

3. **数据展示**
   - 检查会话ID、时间、消息内容是否正确显示
   - 检查长文本是否正常换行

### 5.2 边界测试

1. **空数据**
   - 新用户无历史记录时，应显示"暂无历史记录"

2. **网络错误**
   - 断网情况下，应显示错误提示

3. **Token过期**
   - Token过期时，应自动跳转到登录页

## 六、注意事项

1. **Token认证**
   - 所有接口需要Bearer Token
   - Token存储在 `access_token` key中
   - Token过期会自动跳转登录页

2. **响应格式**
   - 后端返回格式为 `{code, message, data, error}`
   - 前端需要从 `response.data` 中获取实际数据

3. **分页参数**
   - `page_size` 最大值为100
   - 默认 `page=1`, `page_size=20`

4. **时间格式**
   - 后端返回ISO8601格式（UTC）
   - 前端已做格式化处理，显示相对时间

## 七、联调检查清单

- [ ] 历史记录列表能正常加载
- [ ] 搜索功能正常工作
- [ ] 分页功能正常
- [ ] 时间显示正确
- [ ] 空状态提示正常
- [ ] Token过期处理正常
- [ ] 网络错误处理正常
- [ ] 页面样式正常

