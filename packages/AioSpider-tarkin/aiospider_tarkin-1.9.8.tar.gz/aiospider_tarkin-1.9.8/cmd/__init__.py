def aiospider_help():
    from pathlib import Path
    help_text = (Path(__file__).parent / 'help.txt').read_text(encoding='utf-8')
    print(help_text)


def aiospider_version():
    from AioSpider import __version__
    print(f'AioSpider的当前版本：{__version__}')


def spider_list():
    import ast
    from pathlib import Path

    def is_spider_class(node):
        return (
                isinstance(node, ast.ClassDef) and
                any(base.id == 'Spider' for base in node.bases) and
                node.name != 'Spider'
        )

    def get_spiders_from_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read())
        return {node.name for node in ast.walk(tree) if is_spider_class(node)}

    def get_spiders_from_path(path):
        spiders = set()
        if path.is_file() and path.suffix == '.py' and path.stem != '__init__':
            spiders.update(get_spiders_from_file(path))
        elif path.is_dir():
            for sub_path in path.iterdir():
                spiders.update(get_spiders_from_path(sub_path))
        return spiders

    spiders = set()
    current_dir = Path.cwd()

    if current_dir.name == 'spiders':
        spider_dir = current_dir
    else:
        spider_dir = current_dir / 'spiders'

    if not spider_dir.exists():
        print('没有找到spiders目录，请检查是否切换到项目路径！')
        return

    spiders.update(get_spiders_from_path(spider_dir))

    if spiders:
        print('项目中所有爬虫：\n' + '\n'.join(sorted(spiders)))
    else:
        print('没有找到任何爬虫！')

def create_project(project_name):
    from AioSpider.template import gen_project

    for item in gen_project(project_name):
        if item['type'] == 'dir':
            item['path'].mkdir(parents=True, exist_ok=True)
        else:
            item['path'].write_text(item['text'], encoding='utf-8')

    print(f'项目 {project_name} 创建成功')


def create_spider(spider_name, spider_url, spider_source, spider_target, spider_help):
    from pathlib import Path
    from AioSpider.template import gen_spider

    spider_text = gen_spider(spider_name, spider_url, spider_source, spider_target, spider_help)
    path = Path.cwd() / f'{spider_name}.py'
    path.write_text(spider_text, encoding='utf-8')
    print(f'爬虫 {spider_name} 创建成功')


def start_server():
    import os
    from pathlib import Path
    from AioSpider.tools import execute_command, get_ipv4

    try:
        import AioServer
    except ImportError:
        print('AioServer 未安装，请pip安装[pip install AioServer-zly]')
        return

    cwd = Path.cwd()

    os.chdir(Path(AioServer.__file__).parent)
    pid = execute_command(f'start /B uvicorn main:app --host {get_ipv4()} --port 10010', close=True)
    os.chdir(cwd)

    print(f'{get_ipv4()}:10010 启动成功')


def stop_server():
    from AioSpider.tools import kill_process_by_port, get_ipv4

    kill_process_by_port(10010)
    print(f'{get_ipv4()}服务器关闭成功')


def check_redis():
    from AioSpider.tools import is_port_in_use
    if is_port_in_use(port=6379):
        print('redis 服务启动成功：127.0.0.1:6379')
    else:
        print('redis 服务未启动')
def crawl_spider(spider_name):
    from .crawl import CrawlCommand
    from .cmd import CommandName

    command = CrawlCommand()
    command.add_name(CommandName(spider_name))
    command.execute()


def test_proxy(proxy, duration: int = 5):
    import time
    import requests

    url = 'https://797b822149c93a03ed0c1104e08a0f57.dlied1.cdntips.net/dldir1.qq.com/weixin/Windows/WeChatSetup' \
          '.exe?mkey=6454e52edfa67215&f=8f07&cip=223.166.84.224&proto=https&sche_svr=lego_ztc'

    start_time = time.time()
    proxies = {'http': proxy, 'https': proxy}
    total_bytes = 0

    try:
        with requests.get(url, proxies=proxies, stream=True, timeout=duration) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
                elapsed_time = time.time() - start_time
                if elapsed_time > duration:
                    break
    except requests.RequestException as e:
        print(f"IP{proxy if proxy else '本机'} 测试失败，原因: {e}")
        return None

    print(
        f'测试成功：IP({proxy if proxy else "本机"})的带宽为 {round(total_bytes / elapsed_time / (1024 ** 2), 2)} MB/s')


def mysql_to_orm(input_path, output_path):
    import re
    from pathlib import Path

    def execute(in_path=None, out_path=None):

        if in_path is None:
            in_path = Path('utils/table.txt')
            if not in_path.exists():
                print('未输入sql文件路径[aioSpider -help 查看帮助]')
                return
        else:
            in_path = Path(in_path)

        sql = in_path.read_text(encoding='utf-8')
        table_name, fields, doc, indexes = _parse_sql(sql)
        model_str = _generate_model(table_name, fields, doc, indexes)
        _write_model(out_path, model_str)

    def _parse_sql(sql):
        if 'create' not in sql.lower():
            print('aioSpider make 输入的建表sql语句错误[aioSpider -help 查看帮助]')
            return

        table_name = re.findall(r'TABLE\s+`?(\w+)`?', sql, re.I)
        if not table_name:
            print('aioSpider make 输入的建表sql语句错误[aioSpider -help 查看帮助]')
            return

        table_name = ''.join(word.title() for word in table_name[0].split('_'))

        # 提取表定义中的字段部分（排除 PRIMARY KEY, UNIQUE KEY, KEY 等）
        table_def_match = re.search(r'CREATE TABLE.*?\((.*)\).*?ENGINE', sql, re.S | re.I)
        if not table_def_match:
            print('aioSpider make 输入的建表sql语句错误[aioSpider -help 查看帮助]')
            return

        table_def = table_def_match.group(1)

        # 按行分割，过滤出字段定义（排除 KEY, PRIMARY KEY 等）
        fields = []
        for line in table_def.split('\n'):
            line = line.strip()
            # 跳过空行和索引定义
            if not line or line.upper().startswith('PRIMARY KEY') or line.upper().startswith('UNIQUE KEY') or line.upper().startswith('KEY') or line.upper().startswith('INDEX'):
                continue
            # 移除末尾的逗号
            line = line.rstrip(',')
            if line:
                fields.append(line)

        doc = re.findall(r"COMMENT='(.*?)'", sql.split('\n')[-1])
        doc = doc[0] if doc else None

        # 解析索引信息
        indexes = {
            'unique': set(),
            'index': set(),
            'composite_unique': []
        }

        for line in sql.split('\n'):
            # 解析 UNIQUE KEY
            unique_match = re.findall(r'UNIQUE KEY.*?\((.*?)\)', line, re.I)
            if unique_match:
                for match in unique_match:
                    cols = [c.strip().strip('`') for c in match.split(',')]
                    if len(cols) > 1:
                        # 联合唯一索引
                        indexes['composite_unique'].append(tuple(cols))
                    else:
                        # 单字段唯一索引
                        indexes['unique'].add(cols[0])

            # 解析普通索引 KEY
            key_match = re.findall(r'^\s*KEY.*?\((.*?)\)', line, re.I)
            if key_match:
                for match in key_match:
                    cols = [c.strip().strip('`') for c in match.split(',')]
                    # 联合索引的第一个字段也添加 index=True
                    if cols:
                        indexes['index'].add(cols[0])

        return table_name, fields, doc, indexes

    def _generate_model(table_name, fields_list, doc, indexes):
        model_str = f'class {table_name}Model(Model):\n'
        if doc:
            model_str += f'    """{doc}数据结构"""\n\n'

        # 生成字段定义
        field_names = []
        for field in fields_list:
            field_def, field_name = _parse_field(field, indexes)
            if field_def:
                model_str += f'    {field_def}\n'
                if field_name:
                    field_names.append(field_name)

        # 添加 order 列表
        if field_names:
            model_str += '\n    order = [\n'
            model_str += '        '
            model_str += ', '.join([f"'{name}'" for name in field_names])
            model_str += '\n    ]\n'

        # 添加 Meta 类（如果有联合唯一索引）
        if indexes.get('composite_unique'):
            model_str += '\n    class Meta:\n'
            model_str += '        composite_unique_indexes = (\n'
            for cols in indexes['composite_unique']:
                model_str += f"            {tuple(cols)},\n"
            model_str += '        )\n'

        return model_str

    def _parse_field(field, indexes):
        # 跳过 id, source, create_time, update_time 字段
        parts = field.split()
        if not parts:
            return None, None

        name = parts[0].strip('`')
        if name in ['id', 'source', 'create_time', 'update_time']:
            return None, None

        if len(parts) < 2:
            return None, None

        field_type = parts[1].lower()

        # 提取注释作为字段名称 - 支持单引号和双引号
        comment = re.findall(r"COMMENT\s+['\"](.+?)['\"]", field, re.I)
        field_name = comment[0] if comment else name

        # 构建参数列表（顺序：name, max_length/precision, index/unique, null）
        kwargs_parts = []
        kwargs_parts.append(f'name="{field_name}"')

        # varchar/char 的 max_length
        if 'varchar' in field_type or 'char' in field_type:
            max_length = re.findall(r'\((\d+)\)', field_type)
            if max_length:
                kwargs_parts.append(f'max_length={max_length[0]}')

        # decimal 的 max_length 和 precision 参数
        if 'decimal' in field_type:
            precision_match = re.findall(r'decimal\((\d+),(\d+)\)', field_type)
            if precision_match:
                total_digits = int(precision_match[0][0])
                decimal_places = int(precision_match[0][1])
                # 如果总位数大于10，添加 max_length 参数
                if total_digits > 10:
                    kwargs_parts.append(f'max_length={total_digits}')
                # 添加 precision (小数位数)
                if decimal_places > 0:
                    kwargs_parts.append(f'precision={decimal_places}')
                # 对于大数字字段，添加 allow_int=True
                if total_digits > 10:
                    kwargs_parts.append('allow_int=True')

        # 检查是否有唯一索引
        if name in indexes.get('unique', set()):
            kwargs_parts.append('unique=True')
        # 检查是否有普通索引
        elif name in indexes.get('index', set()):
            kwargs_parts.append('index=True')

        # 处理 NULL
        is_not_null = 'not null' in field.lower()
        has_default = 'default' in field.lower() and 'default null' not in field.lower()

        # 只有当字段允许 NULL 且没有默认值（或默认值为 NULL）时才添加 null=True
        if not is_not_null or 'default null' in field.lower():
            kwargs_parts.append('null=True')

        # 处理日期字段的特殊属性
        if field_type == 'date':
            kwargs_parts.append('allow_string=True')

        kwargs_str = ', '.join(kwargs_parts)

        # 根据类型生成字段定义
        if 'auto_increment' in field.lower():
            return None, None  # 跳过自增ID字段
        elif 'bigint' in field_type:
            return f"{name} = fields.BigIntField({kwargs_str})", name
        elif 'int' in field_type:
            return f"{name} = fields.IntField({kwargs_str})", name
        elif 'float' in field_type or 'double' in field_type:
            return f"{name} = fields.FloatField({kwargs_str})", name
        elif 'decimal' in field_type:
            return f"{name} = fields.DecimalField({kwargs_str})", name
        elif 'varchar' in field_type or 'char' in field_type:
            return f"{name} = fields.CharField({kwargs_str})", name
        elif 'text' in field_type:
            return f"{name} = fields.TextField({kwargs_str})", name
        elif 'timestamp' in field_type or 'datetime' in field_type:
            return None, None  # 跳过 timestamp/datetime
        elif field_type == 'date':
            return f"{name} = fields.DateField({kwargs_str})", name
        else:
            return None, None

    def _write_model(out_path, model_str):
        if out_path is None:
            out_path = Path('models') / f'{table_name.lower()}.py' if Path('models').exists() else Path(
                f'{table_name.lower()}.py')
        else:
            out_path = Path(out_path)
        out_path.write_text(model_str, encoding='utf-8')

    execute(input_path, output_path)


def curl_to_spider(input_path, output_path):
    import re
    import json
    from pathlib import Path

    def parse_curl(curl_command):
        url_pattern = r"'(https?://[^']+)'"
        header_pattern = r'-H\s*"([^:]+):\s*([^"]+)"'
        data_pattern = r"--data-raw\s*'(.+)'"

        url = re.search(url_pattern, curl_command).group(1)
        headers = dict(re.findall(header_pattern, curl_command))
        data = re.search(data_pattern, curl_command)
        data = data.group(1) if data else None

        method = 'POST' if data else 'GET'

        return url, headers, data, method

    def generate_spider_code(url, headers, data, method):
        code = f"""import requests

url = '{url}'
headers = {json.dumps(headers, indent=4)}
data = {json.dumps(data) if data else None}

response = requests.{method.lower()}(url, headers=headers{', data=data' if data else ''})

print(response.status_code)
print(response.text)
"""
        return code

    curl_command = Path(input_path).read_text(encoding='utf-8')
    url, headers, data, method = parse_curl(curl_command)
    spider_code = generate_spider_code(url, headers, data, method)

    if output_path:
        Path(output_path).write_text(spider_code, encoding='utf-8')
    else:
        print(spider_code)


