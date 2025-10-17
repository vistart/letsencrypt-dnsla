# 修改解析状态

## Request

### 请求示例

```http
PUT /api/recordDisable HTTP/1.1
Authorization: Basic {token}
Content-Type: application/json; charset=utf-8

{
	"id":"85369994254488576",
    "disable": false
}
```

### 请求参数

| 参数    | 名称   | 类型   | 必选 |
|---------|--------|--------|------|
| id      | 域名id | string | YES  |
| disable | 是否暂停 | bool   | NO   |

## Response

### 响应示例

```json
{
    "code":200,
    "msg":"",
    "data":null
}
```