# 查询解析记录列表

## Request

### 请求示例

```http
GET /api/recordList?pageIndex=1&pageSize=10&domainId=85371689655342080 HTTP/1.1
Authorization: Basic {token}
```

### 请求参数

> **注意**: 筛选所有时，可选参数不要传，例如筛选所有分组解析记录：
> 
> 错误示例: `/api/recordList?pageIndex=1&pageSize=10&groupId=` 本实例会筛选所有默认分组
> 
> 正确示例: `/api/recordList?pageIndex=1&pageSize=10`

| 参数      | 名称                                           | 类型   | 必选 |
|-----------|------------------------------------------------|--------|------|
| pageIndex | 当前页码                                       | int    | YES  |
| pageSize  | 当前页数据条数                                 | int    | YES  |
| domainId  | 域名id                                         | string | YES  |
| type      | 记录类型                                       | int    | NO   |
| groupId   | 解析记录分组id,默认分组为空字符串             | string | NO   |
| lineId    | 线路id,参考线路文档                           | string | NO   |
| host      | 主机头                                         | string | NO   |
| data      | 记录值                                         | string | NO   |
| disable   | 是否暂停                                       | bool   | NO   |
| system    | 是否系统解析,域名添加时系统会生成默认NS记录   | bool   | NO   |
| dominant  | 是否显性URL转发,仅针对URL，配合类型使用查询显性URL转发或隐性URL转发 | bool   | NO   |

### 记录类型

| 记录类型 | 值   |
|----------|------|
| A        | 1    |
| NS       | 2    |
| CNAME    | 5    |
| MX       | 15   |
| TXT      | 16   |
| AAAA     | 28   |
| SRV      | 33   |
| CAA      | 257  |
| URL转发  | 256  |

## Response

### 响应示例

```json
{
    "code": 200,
    "msg": "",
    "data": {
        "total": 1,
        "results": [
            {
                "id": "85394988049110016",
                "createdAt": 1692862151,
                "updatedAt": 1692862151,
                "domainId": "85371689655342080",
                "groupId": "",
                "groupName": "",
                "host": "www",
                "displayHost": "www",
                "type": 1,
                "lineId": "",
                "lineCode": "",
                "lineName": "",
                "data": "1.1.1.1",
                "displayData": "1.1.1.1",
                "ttl": 600,
                "weight": 1,
                "preference": 1,
                "domaint": false,
                "system": false,
                "disable": false
            }
        ]
    }
}
```

### 响应参数

| 参数         | 说明                         |
|--------------|------------------------------|
| total        | 总条数                       |
| id           | 域名id                       |
| createdAt    | 域名添加时间 Unix 时间戳     |
| updatedAt    | 域名最后修改时间 Unix 时间戳 |
| domainId     | 域名id                       |
| groupId      | 分组id,空为默认分组           |
| groupName    | 分组名称,空为默认分组         |
| host         | Punycode 编码后的主机头      |
| displayHost  | Punycode 编码前的主机头      |
| type         | 记录类型                     |
| lineId       | 线路id，参考线路文档         |
| lineCode     | 线路code，参考线路文档       |
| lineName     | 线路名称，参考线路文档       |
| data         | Punycode 编码后的记录值      |
| displayData  | Punycode 编码前的记录值      |
| ttl          | TTL                          |
| weight       | 权重                         |
| preference   | MX优先级                     |
| domaint      | 是否显性URL转发              |
| system       | 是否系统解析记录             |
| disable      | 是否暂停                     |