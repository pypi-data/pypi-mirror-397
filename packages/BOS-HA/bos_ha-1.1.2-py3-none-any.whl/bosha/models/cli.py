#!/usr/bin/env python3
"""
模型管理命令行界面

支持以下子命令：
- list: 列出所有可用模型
- list-available: 列出所有可下载模型
- select: 选择要使用的模型
- download: 下载模型
- info: 显示当前使用的模型信息
- interactive: 交互式选择并下载模型
"""

import argparse
import sys
from bosha.models.model_manager import ModelManager
from bosha.utils.i18n import set_language, gettext as _

def main():
    """主函数"""
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description=_("BOS-HA模型管理工具"))
    
    # 全局参数
    parser.add_argument("--lang", choices=["zh", "en"], help=_("设置语言"))
    subparsers = parser.add_subparsers(dest="command", help=_("子命令帮助"))
    
    # list 子命令
    list_parser = subparsers.add_parser("list", help=_("列出所有可用模型"))
    list_parser.add_argument("--type", help=_("按类型过滤模型，可选值：pytorch, onnx, openvino"))
    list_parser.add_argument("--all", action="store_true", help=_("列出所有模型，包括已下载和未下载的"))
    
    # list-available 子命令
    list_available_parser = subparsers.add_parser("list-available", help=_("列出所有可下载模型"))
    
    # select 子命令
    select_parser = subparsers.add_parser("select", help=_("选择要使用的模型"))
    select_parser.add_argument("model_name", help=_("模型名称"))
    
    # download 子命令
    download_parser = subparsers.add_parser("download", help=_("下载模型"))
    download_parser.add_argument("model_names", nargs="*", help=_("要下载的模型名称列表"))
    download_parser.add_argument("--url", help=_("模型下载URL，默认为配置中的URL"))
    download_parser.add_argument("--all", action="store_true", help=_("下载所有可下载模型"))
    download_parser.add_argument("--force", action="store_true", help=_("强制重新下载已存在的模型"))
    download_parser.add_argument("--max-workers", type=int, default=3, help=_("并发下载的最大工作线程数"))
    
    # info 子命令
    info_parser = subparsers.add_parser("info", help=_("显示当前使用的模型信息"))
    info_parser.add_argument("model_name", nargs="?", help=_("模型名称，默认为当前模型"))
    
    # validate 子命令
    validate_parser = subparsers.add_parser("validate", help=_("验证模型是否有效"))
    validate_parser.add_argument("model_name", nargs="?", help=_("要验证的模型名称，默认为所有已下载模型"))
    
    # interactive 子命令
    interactive_parser = subparsers.add_parser("interactive", help=_("交互式选择并下载模型"))
    interactive_parser.add_argument("--download-only", action="store_true", help=_("只下载模型，不选择使用"))
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 设置语言
    if args.lang:
        set_language(args.lang)
    
    # 创建模型管理器
    manager = ModelManager()
    
    
    # 根据命令执行相应操作
    if args.command == "list":
        # 列出所有可用模型
        if args.all:
            models = manager.list_all_models()
            print(_("所有模型："))
            print()
            for model in models:
                print(f"{model['name']}:")
                print(f"  {_("状态")}: {model['status']}")
                if model['status'] == _("已下载"):
                    print(f"  {_("路径")}: {model['path']}")
                    print(f"  {_("大小")}: {model['size_human']}")
                    print(f"  {_("类型")}: {model['type']}")
                print(f"  {_("架构")}: {model['arch']}")
                print(f"  {_("描述")}: {model['description'][:50]}...")
                print()
        else:
            models = manager.list_models(model_type=args.type)
            if models:
                print(_("可用模型："))
                print()
                for model in models:
                    print(f"{model['name']}:")
                    print(f"  {_("路径")}: {model['path']}")
                    print(f"  {_("大小")}: {model['size_human']}")
                    print(f"  {_("类型")}: {model['type']}")
                    print(f"  {_("架构")}: {model['arch']}")
                    print(f"  {_("描述")}: {model['description'][:50]}...")
                    print()
            else:
                print(_("没有可用模型，请先下载或添加模型"))
    
    elif args.command == "list-available":
        # 列出所有可下载模型
        available_models = manager.list_available_models()
        if available_models:
            print(_("可下载模型："))
            print()
            for model_id, model_info in available_models.items():
                print(f"{model_id}:")
                print(f"  {_("名称")}: {model_info['name']}")
                print(f"  {_("类型")}: {model_info['type']}")
                print(f"  {_("架构")}: {model_info['arch']}")
                print(f"  {_("描述")}: {model_info['description'][:50]}...")
                print(f"  {_("下载链接")}: {model_info['url']}")
                print()
        else:
            print(_("没有可下载模型"))
    
    elif args.command == "select":
        # 选择模型
        success = manager.select_model(args.model_name)
        if success:
            print(f"{_("已选择模型")}: {args.model_name}")
        else:
            print(f"{_("选择模型失败")}: {args.model_name} {_("不存在")}")
            # 显示可用模型
            models = manager.list_models()
            if models:
                print(_("可用模型："))
                for model in models:
                    print(f"  - {model['name']}")
    
    elif args.command == "download":
        # 下载模型
        if args.all:
            # 下载所有模型（使用并发下载）
            model_paths = manager.download_all(force=args.force, max_workers=args.max_workers)
            print(f"\n=== {_("下载完成")} ===")
            print(f"{_("成功下载")} {len(model_paths)} {_("个模型")}")
        elif args.model_names:
            # 下载多个指定模型（使用并发下载）
            model_paths = manager.download_models(args.model_names, force=args.force, max_workers=args.max_workers)
            print(f"\n=== {_("下载完成")} ===")
            print(f"{_("成功下载")} {len(model_paths)} {_("个模型")}")
        else:
            # 下载单个模型
            model_path = manager.download_model(args.url, force=args.force)
            if model_path:
                print(f"{_("模型下载成功")}: {model_path}")
            else:
                print(_("模型下载失败"))
    
    elif args.command == "info":
        # 显示模型信息
        if args.model_name:
            info = manager.get_model_info(args.model_name)
        else:
            info = manager.get_model_info()
        
        if info:
            print(f"{_("模型信息")}：")
            print(f"  {_("名称")}: {info['name']}")
            print(f"  {_("状态")}: {info['status']}")
            if "path" in info:
                print(f"  {_("路径")}: {info['path']}")
            if "size_human" in info:
                print(f"  {_("大小")}: {info['size_human']}")
            if "type" in info:
                print(f"  {_("类型")}: {info['type']}")
            if "arch" in info:
                print(f"  {_("架构")}: {info['arch']}")
            if "description" in info:
                print(f"  {_("描述")}: {info['description']}")
            if "download_time" in info:
                print(f"  {_("下载时间")}: {info['download_time']}")
            if "url" in info:
                print(f"  {_("下载链接")}: {info['url']}")
        else:
            print(_("模型不存在"))
    
    elif args.command == "validate":
        # 验证模型
        if args.model_name:
            # 验证单个模型
            model_info = manager.get_model_info(args.model_name)
            if model_info and "path" in model_info:
                print(f"=== {_("验证模型")}: {args.model_name} ===")
                result = manager.validate_model(model_info["path"])
                print(f"{_("验证结果")}: {'成功' if result else '失败'}")
            else:
                print(f"{_("模型")} {args.model_name} {_("不存在或未下载")}")
        else:
            # 验证所有已下载模型
            print(f"=== {_("验证所有已下载模型")} ===")
            results = manager.validate_all_models()
            
            success_count = sum(1 for r in results if r["valid"])
            total_count = len(results)
            
            print(f"\n=== {_("验证结果汇总")} ===")
            print(f"{_("总模型数")}: {total_count}")
            print(f"{_("成功")}: {success_count}")
            print(f"{_("失败")}: {total_count - success_count}")
            
            if success_count != total_count:
                print(f"\n{_("失败的模型")}:")
                for result in results:
                    if not result["valid"]:
                        print(f"  - {result['name']} ({result['type']})")
    
    elif args.command == "interactive":
        # 交互式选择并下载模型
        print(f"=== BOS-HA {_("交互式模型管理")} ===")
        print()
        
        # 获取所有模型列表
        all_models = manager.list_all_models()
        
        if not all_models:
            print(_("没有可用模型"))
            sys.exit(1)
        
        # 显示模型列表
        print(_("模型列表:"))
        print("-" * 80)
        for idx, model in enumerate(all_models, 1):
            status = model["status"]
            model_id = model["name"]
            model_name = model.get("name", model_id)
            arch = model.get("arch", "-").ljust(20)
            
            print(f"{idx:2d}. {model_name:<20} {arch} {_("状态")}: {status}")
            if status == _("已下载"):
                print(f"    {_("文件位置")}: {model['path']}")
                print(f"    {_("文件大小")}: {model['size_human']}")
            print(f"    {_("描述")}: {model.get('description', '')}")
            print()
        
        # 用户选择模型
        while True:
            try:
                choice = input(f"{_("请选择模型")} (1-{len(all_models)}, 0 {_("退出")}): ")
                choice = int(choice)
                if choice == 0:
                    print(_("退出交互式模型管理"))
                    sys.exit(0)
                elif 1 <= choice <= len(all_models):
                    break
                else:
                    print(f"{_("请输入")} 1-{len(all_models)} {_("之间的数字")}")
            except ValueError:
                print(_("请输入有效数字"))
        
        # 获取选择的模型
        selected_model = all_models[choice - 1]
        model_name = selected_model["name"]
        
        print(f"\n{_("你选择了")}: {model_name}")
        print(f"{_("当前状态")}: {selected_model['status']}")
        
        if selected_model["status"] == _("已下载"):
            # 模型已下载，询问是否选择使用
            if not args.download_only:
                use_choice = input(f"{_("模型")} {model_name} {_("已下载，是否将其设为当前使用的模型？")} (y/n): ")
                if use_choice.lower() == 'y':
                    success = manager.select_model(model_name)
                    if success:
                        print(f"{_("已成功将")} {model_name} {_("设为当前使用的模型")}")
                    else:
                        print(f"{_("设置模型失败")}")
        else:
            # 模型未下载，询问是否下载
            download_choice = input(f"{_("模型")} {model_name} {_("未下载，是否下载？")} (y/n): ")
            if download_choice.lower() == 'y':
                # 下载模型
                model_path = manager.download_model(model_name=model_name)
                if model_path:
                    print(f"{_("模型")} {model_name} {_("下载成功")}")
                    # 询问是否选择使用
                    if not args.download_only:
                        use_choice = input(f"{_("是否将")} {model_name} {_("设为当前使用的模型？")} (y/n): ")
                        if use_choice.lower() == 'y':
                            success = manager.select_model(model_name)
                            if success:
                                print(f"{_("已成功将")} {model_name} {_("设为当前使用的模型")}")
                            else:
                                print(f"{_("设置模型失败")}")
                else:
                    print(f"{_("模型")} {model_name} {_("下载失败")}")
                    sys.exit(1)
    
    else:
        # 显示帮助信息
        parser.print_help()

if __name__ == "__main__":
    main()
