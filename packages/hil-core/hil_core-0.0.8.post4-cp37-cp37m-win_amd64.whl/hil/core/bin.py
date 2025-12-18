import argparse
import json
import yaml
from loguru import logger
from hil.core import Cantp, UdsClient
from hil.core.doip_client import DoipClient
from hil.bus import load_bus
from hil.common.utils import parser_canid


__version__ = '1.0.0'
__author__ = 'notmmao@gmail.com'

class MyUdsClient(UdsClient):
    def after_recv(self, resp: str, resp_bytes, ctx):
        if resp.startswith("7101"):
            rid_code = resp[4:8]
            rid_value = resp[8:]
            ctx[rid_code.upper()] = rid_value
        if resp[:4] in ["6702", "6704", "6706", "6708", "670A", "6712"]:
            ctx[resp[:4]] = resp[8:]
        return super().after_recv(resp, resp_bytes, ctx)
        

def load_config(fn:str):
    with open(fn, "r", encoding="utf-8") as f:
        if fn.endswith(".json"):
            config = json.load(f)
        else:
            config = yaml.safe_load(f)
        return config

def uds(txid, rxid, cmd_config:str, bus_config:str, extended=False):
    txid = parser_canid(txid)
    rxid = parser_canid(rxid)
    bus = load_bus(bus_config)
    tp = Cantp(bus, txid, rxid, is_extended_id=extended)
    client = MyUdsClient()
    cmds = load_config(cmd_config)
    ctx = {}
    client.run(cmds, tp, ctx, 3)
    bus.shutdown()
    return ctx

def doip(doip_config:str, cmd_config:str):
    cmds = load_config(cmd_config)
    config = load_config(doip_config)
    tp = DoipClient(**config)
    client = MyUdsClient()
    ctx = {}
    client.run(cmds, tp, ctx, 3)
    return ctx

def run_test_file(test_file:str, ctx:dict):
    """执行测试文件并将ctx传入"""
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_code = f.read()
        
        exec_globals = {'ctx': ctx, '__file__': test_file, '__name__': '__main__'}
        
        # 先编译代码检查语法
        compiled = compile(test_code, test_file, 'exec')
        
        # 正常执行非断言部分
        exec_globals_nc = exec_globals.copy()
        try:
            exec(compiled, exec_globals_nc)
        except AssertionError as e:
            # 这里捕获首次断言失败，进行详细分析
            frame = e.__traceback__
            while frame:
                if frame.tb_frame.f_code.co_filename == test_file:
                    lineno = frame.tb_lineno
                    with open(test_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if 0 <= lineno-1 < len(lines):
                            error_line = lines[lineno-1].strip()
                            logger.error(f"测试文件 {test_file} 第{lineno}行失败: {error_line}")
                            # 显示上下文的值
                            # logger.error(f"当前ctx['{error_line.split('[')[1].split(']')[0]}'] = {ctx.get(error_line.split('[')[1].split(']')[0], '键不存在')}")
                    break
                frame = frame.tb_next
            raise
        
        logger.info(f"测试文件 {test_file} 执行完成")
        
    except FileNotFoundError:
        logger.error(f"测试文件 {test_file} 不存在")
        raise
    except Exception as e:
        if not isinstance(e, AssertionError):
            logger.error(f"执行测试文件 {test_file} 失败: {e}")
        raise

def main():
    logger.enable("hil.core")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="protocol")
    can_parser = subparsers.add_parser("can")
    can_parser.add_argument("--txid", "-t", required=True, help="请求CANID")
    can_parser.add_argument("--rxid", "-r", required=True, help="接收CANID")
    can_parser.add_argument("--cmd", "-c", required=True, help="命令序列json或yaml文件")
    can_parser.add_argument("--bus", "-b", required=True, help="CAN总线配置json或yaml文件")
    can_parser.add_argument("--extended", "-e", action="store_true", help="CAN扩展帧")
    
    doip_parser = can_parser = subparsers.add_parser("doip")
    can_parser.add_argument("--node", "-n", required=True, help="DoIP配置yaml文件")
    doip_parser.add_argument("--cmd", "-c", required=True, help="命令序列json或yaml文件")
    doip_parser.add_argument("--test", "-t", required=False, help="test.py文件")

    args = parser.parse_args()
    logger.debug(args)
    if args.protocol == "doip":
        ctx = doip(args.node, args.cmd)
        if args.test:
            run_test_file(args.test, ctx)
        logger.info(ctx)
    elif args.protocol == "can":
        ctx = uds(args.txid, args.rxid, args.cmd, args.bus, args.extended)
        logger.info(ctx)
        if args.test:
            run_test_file(args.test, ctx)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()