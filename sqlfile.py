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
            table_name_match.group(1),
            table_comment_match.group(1) if table_comment_match else ''
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
sql = """CREATE TABLE `tb_operator_record` (
  `id` bigint(20) NOT NULL COMMENT '操作信息主键',
  `update_type` int(11) DEFAULT NULL COMMENT '操作类型(0=账号在职状态 1=修改离职继承 2=停用账号 3=启用账号 4=修改账号信息)',
  `update_id` bigint(20) DEFAULT NULL COMMENT '操作人id',
  `update_name` varchar(32) DEFAULT NULL COMMENT '操作人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  `on_job_state` int(11) DEFAULT NULL COMMENT '账号在职状态(0=在职 1=离职)',
  `operator_id` bigint(20) DEFAULT NULL COMMENT '被操作人id/离职人id',
  `operator_name` varchar(32) DEFAULT NULL COMMENT '被操作人姓名',
  `inherit_id` bigint(20) DEFAULT NULL COMMENT '继承人id',
  `inherit_name` varchar(32) DEFAULT NULL COMMENT '继承人姓名',
  `shop_collect` json DEFAULT NULL COMMENT '离职前分管的客户',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;"""

print(parse_create_table(sql))
