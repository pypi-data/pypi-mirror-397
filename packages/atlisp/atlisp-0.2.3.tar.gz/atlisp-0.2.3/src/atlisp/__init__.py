import sys
import argparse
import tomllib
import pathlib
from .atlisp import install_atlisp,pull,pkglist,remove,search,show_cad,cadapp
#from .search import search
parser = argparse.ArgumentParser(
    prog="atlisp",usage="atlisp command <pkgname/keystring>",
    description='@lisp是一个运行于 AutoCAD、中望CAD、浩辰CAD及类似兼容的CAD系统中的应用管理器。')
parser.add_argument("command",help="执行 atlisp 命令")

version = "0.2.2"
about_str = "@lisp是一个运行于 AutoCAD、中望CAD、浩辰CAD及类似兼容的CAD系统中的应用管理器。"

def main():
    global version;
    # target_function(*args,**kwargs)
    # path = pathlib.Path("pyproject.toml")
    # with  path.open(mode="rb") as  fp:
    #     projectdata=tomllib.load(fp)
    parser = argparse.ArgumentParser()
    parser.add_argument('-a','--app', choices=['AutoCAD', 'ZWCAD', 'GstraCAD',"BricscadApp"],help='指定CAD应用程序')
    parser.add_argument('-v','--cadver', help='指定CAD特定的版本，如浩辰需要指定20-25之间的整数,其它CAD可省略')
    parser.add_argument('-V','--version', action='store_true',help='当前 atlisp 管理器版本')
    subparsers = parser.add_subparsers(title='命令', dest='command')
    install_parser = subparsers.add_parser('install', help='安装 atlisp 到CAD')
    list_parser = subparsers.add_parser('list', help='列出当前已安装的 @lisp 应用包')
    pull_parser = subparsers.add_parser('pull', help='下载安装应用包到 CAD')
    pull_parser.add_argument('pkgname', help='要安装的应用包名称')
    search_parser = subparsers.add_parser('search', help='从网络搜索 @lisp 应用包')
    search_parser.add_argument('keystring', help='要搜索应用包名称或功能说明关键字')
    args = parser.parse_args()

    print(f"{about_str}")
    print("")
    if args.app :
        if args.cadver:
            appid = f"{args.app}.application.{args.cadver}"
        else:
            appid = f"{args.app}.application"
    if args.command  ==  "pull":
        if args.app:
            pull(pkgname=f"{args.pkgname}", acadapp=cadapp(appid=f"{appid}"))
        else:
            pull(pkgname=f"{args.pkgname}")
    elif args.command  ==  "remove":
        remove(f"{args.pkgname}")
    elif args.command == "install":
        print("安装@lisp到 CAD 中")
        if args.app:
            show_cad(install_atlisp(acadapp=cadapp(appid=f"{appid}")))
        else:
            show_cad(install_atlisp())
        print("......完成")
    elif args.command == "list":
        print("已安装的应用包:")
        print("---------------")
        pkglist()
        print("===============")
    elif args.command  ==  "search" :
        search(f"{args.keystring}")
    elif args.version:
        print(f"Version: {version}")
    else:
        print("请输入  atlisp -h 显示帮助信息")
