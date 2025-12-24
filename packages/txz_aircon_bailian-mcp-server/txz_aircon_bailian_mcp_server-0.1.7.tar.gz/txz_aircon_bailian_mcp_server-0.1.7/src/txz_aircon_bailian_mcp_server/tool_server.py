
from typing import Any
from mcp.server.fastmcp import FastMCP
import json
# 若使用OpenAI API，导入官方库；自定义API则用requests即可
from dotenv import load_dotenv

# from pydantic import Field
load_dotenv()
# 初始化 MCP 服务器

mcp = FastMCP("txz_aircon_bailian-mcp-server")

@mcp.tool()
async def page_control(	
    name: str,
    operate: str,
    object: str
) -> str:
    """
    这是一个控制空调页面开关的工具。
    :param query: 用户的输入内容。
    :param object: 协议中的对象，本项为必填项，本工具固定为 page。
    :param name: 页面名称:只能是"空调","空调设置",页面名称中的"空调设置"是指对空调模式以及属性进行设置的页面,页面名称中的"空调"是指空调的显示页面或空调的主界面。
    :param operate: 操作类型:open或close页面。
    :return: 操作结果信息
    """
    # aicon_page = ["空调控制", "空调设置", "空调的控制", "空调的设置"]
    
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    if object is None:
        object = "page"
    

    result = f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    name: {name}\n
    operate: {operate}\n
    """
    
	 # 生成自然语言回复
   
    
    return result

@mcp.tool()
async def power_control(
    operate: str,
    object: str,
    positions: list[str] | None = None,
) -> str:
    """
    控制空调电源的开关状态，只用来处理开关空调,不处理带有模式和其他属性操作,可指定空调位置
    :param object: 控制对象,固定为"aircon"
    :param operate: 操作类型, 可选值的值包括 "open", "close"
    :param positions: 位置名称, 空调作用的位置列表，对应协议中的 positions。如主驾、副驾、前排、后排等。
    :return: 操作结果信息
    """
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    result= f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    positions: {positions}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def aircon_cool_heat_control(
    operate: str,
    object: str,
    limit: str | None = None,
    mode: str | None = None,
    positions: list[str] | None = None,

) -> str:
    """
    控制空调制冷/制热相关模式，包括普通制冷、最大制冷、强力制冷、制热模式,可指定空调位置。
    :param object: 控制对象：制冷或制热功能,固定为"aircon/cooling"(制冷),"aircon/heating"(制热)
    :param operate: 操作类型, 固定为 "open"或者"close"
    :param positions: 位置名称, 空调作用的位置列表，对应协议中的 positions。如主驾、副驾、前排、后排等
    :param limit: 最大/最小等限制值，这里用于最大制冷。对应的值有: "max", "min"
    :param mode: 制冷制热的强度模式,如"强力模式"。对应的值包括: "strong"(强力模式)
    :return: 操作结果信息
    """
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    positions: {positions}\n
    limit: {limit}\n
    mode: {mode}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def seat_heat(
    operate: str,
    mode: str,
    object: str,
    positions: list[str] | None = None,
) -> str:
    """
    控制座椅加热工具，用于控制座椅的加热模式, 可指定座椅位置
    :param object: 座椅对象名称(固定值), 固定为: "seat"
    :param operate: 座椅操作名称(固定值), 可选值为: "open", "close"
    :param mode: 座椅模式名称(固定值), 固定为: "heat"
    :param positios: 座椅位置名称(可选值),如: "第一排", "第二排", "主驾", "副驾"等
    :return: 操作结果信息
    """

    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    positions: {positions}\n
    mode: {mode}\n
    """
    
     # 生成自然语言回复
    
    
    return result


@mcp.tool()
async def circulation_control(
    operate: str,
    mode: str,
    object: str,
) -> str:
    """
    控制空调循环以及空调循环的模式,如打开空调内循环或者外循环,不具备位置信息
    :param operate: 操作类型,"open"(打开) or "close"(关闭)
    :param mode: 空调循环的模式,有"internal"(内循环), "external"(外循环)
    :param object: 空调循环对象名称: "aircon/circulation"
    :return:  操作结果信息
    """

    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    mode: {mode}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def purify_control(
    operate: str,
    object: str,
) -> str:
    """
    控制空调净化功能,如:打开空调净化, 不具备位置信息
    :param operate: 操作类型,"open"(打开) or "close"(关闭)
    :param object: 空调循环对象名称: "air_purify"
    :return:  操作结果信息
    """

    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def fan_speed_control(
    operate: str,
    object: str ,
    attr: str,
    limit: str | None = None,
    value: str | int | None = None,
    unit: str | None = None,
    positions: list[str] | None = None,
) -> str:
    """
    控制空调风速的功能, 如:空调风速调大一些,可以选择位置信息
    :param object: 操作对象名,固定为空调 "aircon"
    :param attr: 操作对象的属性名,固定为风速 "speed"
    :param operate: 操作类型,可以选择的值有:调到/设置到"set", 增高"inc", 降低"dec"
    :param value: 风速的具体值,如10%,百分之10,百分之十,10等数值,如果说了单位(百分之,%等)需要有unit参数
    :param limit: 风速的程度,例如 低"low"、中"mid"、高"high"、最大"max"、最小"min"、一些"little"或更多"more",如果说了单位(挡,档)需要有unit参数
    :param unit: 风速单位: "挡","percent"
    position: 需要调整的空调风速所在车的哪个位置，如: "第一排", "第二排", "主驾", "副驾"等
    """
    valid_operate = {"set", "inc", "dec"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    


    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    attr: {attr}\n
    operate: {operate}\n
    value: {value}\n
    limit: {limit}\n
    unit: {unit}\n
    positions: {positions}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def temperature_control(
    operate: str,
    object : str,
    attr: str ,
    value: str | int | None = None,
    unit: str | None = None,
    limit: str | None = None,
    positions: list[str] | None = None,
) -> str:
    
    """
    空调温度调节功能,如:空调温度调到最大,可以选择位置信息
    :param object: 操作对象名,固定为空调 "aircon"
    :param attr: 操作对象的属性名,固定为风速 "temperature"
    :param operate: 操作类型,可以选择的值有:调到/设置到"set", 增高"inc", 降低"dec",(切换/调节)"switch"
    :param value: 温度的具体值,如10,如果说了单位("度")需要有unit参数
    :param limit: 温度的程度,例如 低"low"、中"mid"、高"high"、最大"max"、最小"min"、一些"little"或更多"more",如果说了单位(挡,档)需要有unit参数,如:空调温度调高一些，其中一些是limit的关键词，需要调用limit
    :param unit: 温度单位: "挡","度"
    :param position: 需要调整的空调风速所在车的哪个位置，如: "第一排", "第二排", "主驾", "副驾"等
    """

    valid_operate = {"set", "inc", "dec", "switch"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"

    
    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    attr: {attr}\n
    operate: {operate}\n
    value: {value}\n
    limit: {limit}\n
    unit: {unit}\n
    positions: {positions}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def airflow_control(
    operate: str,
    object: str,
    positions: list[str] | None = None,
    mode: str | None = None
) -> str:
    """
    空调出风模式控制功能,如:空调设置为吹窗吹脚,可以选择位置信息
    :param object: 操作对象名,固定为空调 "aircon"
    :param mode: 空调出风模式的类型: 吹脸"toward_head", 吹脚"toward_feet", 吹窗"toward_window",吹脸吹脚"toward_head_and_feet", 吹窗吹脚"toward_window_and_feet",吹头吹窗"toward_head_and_window",吹头吹脚"toward_head_and_feet_and_window",避人吹"avoid_swing",自由风/自动扫风"auto_swing",对人吹"toward_person",左右扫风"horizontal_swing",上下扫风"vertical_swing"
    :param operate: 操作类型,可以选择的值有:"open", "close", "switch"
    :param position: 需要调整的空调出风模式所在车的哪个位置，如: "第一排", "第二排", "主驾", "副驾"等
    """

    valid_operate = {"open", "close", "switch"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    

    result = f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    mode: {mode}\n
    positions: {positions}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def aircon_mode_control(
    operate: str,
    object: str,
    positions: list[str] | None = None,
    mode: str | None = None
):
    """
    空调模式控制功能,如:空调设置为自动模式,可以选择位置信息
    :param object: 操作对象名,固定为空调 "aircon"
    :param mode: 空调出风模式的类型: 自动/auto"aircon_auto",手动"manual",智能"aircon_smart_mode",爱心提醒"kind_reminder",极速除味"deodorization_rapid",单席"aircon_single_seat",急速降温"aircon_cooling_rapid",过热保护"overheat_protection",座舱降温"cabin_cooling"
    :param operate: 操作类型,可以选择的值有:"open", "close"
    :param position: 需要调整的空调出风模式所在车的哪个位置，如: "第一排", "第二排", "主驾", "副驾"等
    """
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    
    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    mode: {mode}\n
    positions: {positions}\n
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def defog_control(
    operate: str,
    mode: str,
    object: str,
    limit: str | None = None,
) -> str:
    """
    空调除雾控制功能,如:空调设置为后除雾
    :param object: 操作对象名,固定为空调 "aircon"
    :param operate: 操作类型,可选值为 "open"、"close"
    :param mode: 空调的除雾模式,可选值为 除雾"defog", 前除雾"defog/front", 后除雾"defog/back", 前后除雾"defog/all"
    除雾模式的附加模式可选值为:(快速)"rapid",(强力)"strong",(自动)"auto",这些附加模式添加在各种除雾模式的后面,例如:(快速前除雾)"defog/front/rapid"
    :param limit:空调的各种除雾模式的强度模式，可选值为 (最大)"max",(最小)"min",(高挡)"high_level",(中挡)"mid",(低挡)"low_level"
    """
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    
    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    mode: {mode}\n
    limit:{limit}
    """
     # 生成自然语言回复
    
    
    return result

@mcp.tool()
async def defrost_control(
    operate: str,
    mode: str,
    object: str,
    limit: str | None = None,
) -> str:
    """
    空调除霜控制功能,如:空调设置为前后除霜
    :param object: 操作对象名,固定为空调 "aircon"
    :param operate: 操作类型,可选值为 "open"、"close"
    :param mode: 空调的各种除霜模式以及除霜模式的附加模式,空调的各种除霜模式可选值为 (除霜)"defrost", (前除霜)"defrost/front", (后除霜)"defrost/back", (前后除霜)"defrost/all",
    除霜模式的附加模式可选值为:(快速)"rapid",(强力)"strong",(自动)"auto",这些附加模式添加在各种除霜模式的后面,例如:(快速前除霜)"defrost/front/rapid"
    :param limit:空调的各种除霜模式的强度模式，可选值为 (最大)"max",(最小)"min",(高挡)"high_level",(中挡)"mid",(低挡)"low_level"
    """
    valid_operate = {"open", "close"}
    if operate not in valid_operate:
        return f"无效的操作类型,:operate 必须是 {valid_operate} 中的一个"
    
    result =  f"""
    如下是操作页面所需的槽位信息:
    object: {object}\n
    operate: {operate}\n
    mode: {mode}\n
    limit:{limit}
    """
     # 生成自然语言回复
    
    
    return result


def run():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    run()