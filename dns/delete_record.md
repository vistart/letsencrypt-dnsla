# 删除解析记录

## Request

### 请求示例

```http
DELETE /api/record?id=85371689655342080 HTTP/1.1
Authorization: Basic {token}
```

### 请求参数

| 参数 | 名称       | 类型   | 必选 |
|------|------------|--------|------|
| id   | 解析记录id | string | YES  |

## Response

### 响应示例

```json
{
    "code":200,
    "msg":"",
    "data":null
}
```