import re

def parse_create_table(sql):
    # 提取表名和注释
    table_name_match = re.search(r'CREATE TABLE `(\w+)`', sql)
    table_comment_match = re.search(r"COMMENT='([^']*)'", sql)
    
    # 提取字段定义
    fields_section = re.search(r'\((.*?)\)\s*ENGINE', sql, re.DOTALL)
    fields_str = fields_section.group(1).strip()
    
    # 分割字段和索引
    field_lines = [line.strip().strip(',') for line in fields_str.split('\n') if line.strip()]
    
    # 解析字段
    fields = []
    indexes = []
    for line in field_lines:
        if line.startswith(('PRIMARY KEY', 'KEY', 'UNIQUE')):
            # 处理索引
            index_type = 'PRIMARY KEY' if 'PRIMARY KEY' in line else 'INDEX'
            index_name_match = re.search(r'`(\w+)`', line)
            index_name = index_name_match.group(1) if index_name_match else ''
            columns_match = re.findall(r'`(\w+)`', line)
            columns = ', '.join(columns_match)
            indexes.append({
                'index_name': index_name,
                'index_type': index_type,
                'columns': columns
            })
            continue
        if '`' not in line:
            continue
        
        # 提取字段名
        field_name = re.search(r'`(\w+)`', line).group(1)
        
        # 提取类型和长度
        type_match = re.search(r'`\w+`\s+(\w+)(?:\((\d+)\))?', line)
        data_type = type_match.group(1)
        length = type_match.group(2) or ''
        
        # 是否允许NULL
        nullable = 'Y' if 'DEFAULT NULL' in line or 'NULL' in line else 'N'
        
        # 键类型
        key_type = 'PK' if 'AUTO_INCREMENT' in line else ''
        
        # 默认值
        default_match = re.search(r'DEFAULT (\S+)', line)
        default_value = default_match.group(1) if default_match else ''
        
        # 注释
        comment_match = re.search(r"COMMENT\s+'([^']*)'", line)
        comment = comment_match.group(1) if comment_match else ''
        
        fields.append({
            'field_name': field_name,
            'data_type': data_type,
            'length': length,
            'nullable': nullable,
            'key_type': key_type,
            'default_value': default_value,
            'comment': comment
        })
    
    # 构建表格
    table = [
        "### **表名**  \n`{}`（{}）\n".format(
            table_comment_match.group(1) if table_comment_match else '',
            table_name_match.group(1)
        ),
        "| 字段名 | 类型 | 长度/精度 | 允许空 | 键 | 默认值 | 说明 |",
        "|--------|------|-----------|--------|----|--------|------|"
    ]
    
    for field in fields:
        row = "| `{field_name}` | {data_type} | {length} | {nullable} | {key_type} | {default_value} | {comment} |".format(
            field_name=field['field_name'],
            data_type=field['data_type'],
            length=field['length'] if field['length'] else '-',
            nullable=field['nullable'],
            key_type=field['key_type'],
            default_value=field['default_value'] if field['default_value'] else '-',
            comment=field['comment']
        )
        table.append(row)
    
    # 添加索引信息
    if indexes:
        table.append("\n **索引信息**\n")
        table.append("| 索引名 | 类型 | 列 |")
        table.append("|--------|------|----|")
        for index in indexes:
            row = "| `{index_name}` | {index_type} | {columns} |".format(
                index_name=index['index_name'],
                index_type=index['index_type'],
                columns=index['columns']
            )
            table.append(row)
    
    return '\n'.join(table)

# 示例用法
sql = """CREATE TABLE `tb_settler_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '入驻商id',
  `settler_name` varchar(64) DEFAULT NULL COMMENT '入驻商名称',
  `settler_no` varchar(22) DEFAULT NULL COMMENT '入驻商编号',
  `settler_contract` varchar(64) DEFAULT NULL COMMENT '联系人',
  `settler_mobile` varchar(11) DEFAULT NULL COMMENT '联系电话',
  `fixed_number` varchar(255) DEFAULT NULL COMMENT '固定电话',
  `login_account` varchar(64) DEFAULT NULL COMMENT '登录账号',
  `address` varchar(255) DEFAULT NULL COMMENT '入驻商地址',
  `settled_type` int(11) DEFAULT '0' COMMENT '入驻类型：0（默认）：经销商入驻',
  `settled_level` int(11) DEFAULT '0' COMMENT '入驻等级：0（默认）',
  `percentage` int(11) DEFAULT NULL COMMENT '平台手续费占比',
  `institutions_id` bigint(20) DEFAULT NULL COMMENT '机构id',
  `is_completed` int(11) DEFAULT '0' COMMENT '是否完善：0：（默认）未完善；1：已完善',
  `is_proprietary` int(11) DEFAULT '1' COMMENT '是否自营 0:非自营 1:自营',
  `is_own` int(11) DEFAULT '0' COMMENT '是否自仓（0：是；1：否）',
  `sale_man_id` bigint(20) DEFAULT NULL COMMENT '业务员id',
  `creator` varchar(255) DEFAULT NULL COMMENT '创建人',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `state` int(11) DEFAULT '0' COMMENT '状态：0：启用（默认）；1：停用',
  `biz_user_id` varchar(50) DEFAULT NULL COMMENT '对接通联的商户号',
  `is_settled_brands` tinyint(2) DEFAULT '0' COMMENT '是否入驻品牌  0否 1是',
  `settled_brands_id` varchar(255) DEFAULT NULL COMMENT '入驻类目 id 逗号分割',
  `settled_institutions` varchar(255) DEFAULT NULL COMMENT '入驻机构id 加逗号分割',
  `freight_template_id` bigint(25) DEFAULT NULL COMMENT '商品上下架关联运费模板id',
  `settled_shop_type` int(1) DEFAULT NULL COMMENT '1公司 2个体户',
  `settle_account_id` bigint(20) DEFAULT NULL COMMENT '结算明细id',
  `effective_time` datetime DEFAULT NULL COMMENT '结算规则生效时间',
  `balance1` decimal(10,2) DEFAULT NULL COMMENT '在线支付余额',
  `balance2` decimal(10,2) DEFAULT NULL COMMENT '在线支付通联余额',
  `settled_type_pm` int(1) DEFAULT NULL COMMENT '1公司 2个体户 3个人入驻',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `institutions_id` (`institutions_id`),
  KEY `state` (`state`)
) ENGINE=InnoDB AUTO_INCREMENT=930 DEFAULT CHARSET=utf8 COMMENT='入驻商信息';"""

print(parse_create_table(sql))
