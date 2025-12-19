import argparse

from AioSpider.cmd import (
    aiospider_help,
    aiospider_version,
    spider_list,
    create_project,
    create_spider,
    start_server,
    stop_server,
    check_redis,
    test_proxy,
    mysql_to_orm,
    curl_to_spider,
    crawl_spider
)


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='AioSpider 命令行工具', add_help=False)
    parser.add_argument('-h', action='store_true', help='显示帮助信息')
    parser.add_argument('-v', action='store_true', help='显示版本信息')
    parser.add_argument('-l', action='store_true', help='列出项目中的所有爬虫')

    subparsers = parser.add_subparsers(dest='command', help='可用的子命令')

    setup_crawl_parser(subparsers)
    setup_create_parser(subparsers)
    setup_server_parser(subparsers)
    setup_test_parser(subparsers)
    setup_tool_parser(subparsers)

    return parser


def setup_crawl_parser(subparsers):
    crawl_parser = subparsers.add_parser('crawl', help='运行指定的爬虫')
    crawl_parser.add_argument('spider_name', type=str, help='爬虫名称')


def setup_create_parser(subparsers):
    create_parser = subparsers.add_parser('create', help='创建项目或爬虫')
    create_parser.add_argument('-p', type=str, help='项目名称')
    create_parser.add_argument('-s', type=str, help='爬虫名称')
    
    s_group = create_parser.add_argument_group('爬虫相关参数')
    s_group.add_argument('--u', '--url', type=str, help='爬虫起始URL')
    s_group.add_argument('--s', '--source', type=str, dest='source', help='数据源')
    s_group.add_argument('--t', '--target', type=str, help='目标')
    s_group.add_argument('--h', action='store_true', help='显示帮助信息')
    
    create_parser.set_defaults(func=check_spider_args)


def setup_server_parser(subparsers):
    server_parser = subparsers.add_parser('server', help='管理服务器')
    server_parser.add_argument('-s', action='store_true', help='启动服务器')
    server_parser.add_argument('-p', action='store_true', help='停止服务器')
    server_parser.add_argument('-r', action='store_true', help='检查redis是否启动')


def setup_test_parser(subparsers):
    test_parser = subparsers.add_parser('test', help='测试功能')
    test_parser.add_argument('test_type', choices=['proxy'], help='测试类型')
    test_parser.add_argument('-p', type=str, help='代理地址')
    test_parser.add_argument('-d', type=int, default=5, help='测试持续时间（默认5秒）')


def setup_tool_parser(subparsers):
    tool_parser = subparsers.add_parser('tool', help='工具')
    tool_parser.add_argument('tool_type', choices=['mysql_to_orm', 'curl_to_spider'], help='工具类型')
    tool_parser.add_argument('-i', type=str, help='输入文件路径')
    tool_parser.add_argument('-o', type=str, help='输出文件路径')


def check_spider_args(args):
    if args.s is None and (args.u or args.source or args.t or args.h):
        raise argparse.ArgumentTypeError("只有在指定'-s'参数时，才能使用'--u'、'--s'、'--t'和'--h'参数。")


def handle_create(args):
    if args.p:
        create_project(args.p)
    elif args.s:
        create_spider(args.s, args.u, args.source, args.t, args.h)
    else:
        raise argparse.ArgumentTypeError("创建命令需要指定'-p'或'-s'参数。")


def handle_server(args):
    if args.s:
        start_server()
    elif args.p:
        stop_server()
    elif args.r:
        check_redis()
    else:
        raise argparse.ArgumentTypeError("服务器命令需要指定'-s'、'-p'或'-r'参数。")


def handle_test(args):
    if args.test_type == 'proxy':
        test_proxy(args.p, args.d)
    else:
        raise argparse.ArgumentTypeError("不支持的测试类型。")


def handle_tool(args):
    if args.tool_type == 'mysql_to_orm':
        mysql_to_orm(args.i, args.o)
    elif args.tool_type == 'curl_to_spider':
        curl_to_spider(args.i, args.o)
    else:
        raise argparse.ArgumentTypeError("不支持的工具类型。")
def handle_crawl(args):
    if args.spider_name:
        crawl_spider(args.spider_name)
    else:
        raise argparse.ArgumentTypeError("运行爬虫命令需要指定爬虫名称。")

def main():
    parser = setup_parser()
    args = parser.parse_args()

    try:
        if args.command == 'create':
            handle_create(args)
        elif args.command == 'server':
            handle_server(args)
        elif args.command == 'test':
            handle_test(args)
        elif args.command == 'tool':
            handle_tool(args)
        elif args.command == 'crawl':
            handle_crawl(args)
        elif args.h:
            aiospider_help()
        elif args.l:
            spider_list()
        elif args.v:
            aiospider_version()
        else:
            aiospider_help()
    except argparse.ArgumentTypeError as e:
        print(f"错误: {str(e)}")
        parser.print_help()


if __name__ == '__main__':
    import os
    import sys

    # sys.argv = ['aioSpider', '-l']
    # sys.argv = ['aioSpider', 'create', '-p', 'testProject']
    # sys.argv = ['aioSpider', 'create', '-s', 'testSpider']
    # sys.argv = ['aioSpider', 'server', '-r']
    sys.argv = ['aioSpider', 'test', 'proxy', '-p', 'http://127.0.0.1:7890']

    # sys.argv = ['aioSpider', 'server', '-r']
    main()
