import json
import traceback
from datetime import datetime
from .uilts import setup_logger
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from sqlalchemy import asc, desc


def format_model_data(model_instance):
    """
    将数据库模型实例格式化为字典，包括其所有的属性。
    :param model_instance: 数据库模型实例
    :return: 格式化后的字典
    """
    data = {}
    for column in model_instance.__table__.columns:
        data[column.name] = getattr(model_instance, column.name)
    return data


def convert_timestamps_in_dict(record):
    """
    将字典中的时间戳或 datetime 对象转换为日期字符串。
    13位时间戳转换为日期字符串，datetime 对象转换为 'YYYY-MM-DD HH:MM:SS' 格式。
    :param record: 字典
    :return: 转换后的字典
    """
    for key, value in record.items():
        if isinstance(value, int) and len(str(value)) == 13:
            # record[key] = datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d %H:%M:%S')
            record[key] = datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
        elif isinstance(value, datetime):
            # 将 datetime 对象转换为 'YYYY-MM-DD HH:MM:SS' 日期格式字符串
            record[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    return record


def find_list_page(query, page_size, page_index):
    """
    分页查询
    :param query: 查询对象
    :param page_size: 页大小
    :param page_index: 页码
    :return: 分页结果
    """
    total_count = query.count()
    current_page = query.limit(page_size).offset((page_index - 1) * page_size).all()
    records = [convert_timestamps_in_dict(format_model_data(product)) for product in current_page]
    total_pages = (total_count + page_size - 1) // page_size
    return {"total_count": total_count, "records": records, "total_pages": total_pages, "total": total_count }


def query_all(query):
    """
    查询全部
    :param query: 查询对象
    :return: 查询结果
    """
    current = query.all()
    records = [convert_timestamps_in_dict(format_model_data(product)) for product in current]
    return {"records": records}


# 新增或者编辑数据
def save_or_update(session, request_body, model, commit=True, primary_key_field="id"):
    """
    新增或者编辑数据，只更新model中存在的属性。
    :param session: SQLAlchemy数据库会话
    :param request_body: 请求体，包含需要更新或新增的数据  这个的字段必须和数据库表的字段一致
    :param model: 数据库模型
    :param commit: 是否自动提交，默认为True
    :param primary_key_field: 主键字段默认是id
    :return: 保存结果，为model的一个实例
    """
    if request_body.get(primary_key_field):

        # 尝试通过ID获取现有记录
        model_instance = session.query(model).get(request_body.get(primary_key_field))
        if model_instance:
            # 更新现有记录的属性
            for key in request_body:
                if hasattr(model_instance, key):
                    # 只有当model实例具有该属性时才更新
                    setattr(model_instance, key, request_body[key])
            if commit:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    setup_logger().error("数据库提交失败:\n%s", traceback.format_exc())
                    raise RuntimeError("数据更新失败") from e
        else:
            # 如果通过ID找不到实例，则返回False
            raise RuntimeError(f"根据 主键定义字段 {primary_key_field} 数据没有找到")
    else:
        # 为新增记录准备一个字典，仅包含模型定义的属性
        valid_fields = {key: value for key, value in request_body.items() if hasattr(model, key)}
        model_instance = model(**valid_fields)
        session.add(model_instance)
        if commit:
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                setup_logger().error("数据库提交失败:\n%s", traceback.format_exc())
                raise RuntimeError("数据更新失败") from e
    return model_instance


# 批量新增数据
def bulk_insert(session: Session, request_body_list, model, commit=True, primary_key_field="id"):
    """
    批量新增或更新数据。
    :param primary_key_field:
    :param session: SQLAlchemy数据库会话
    :param request_body_list: 请求体列表，每个元素包含需要新增或更新的数据
    :param model: 数据库模型
    :param commit: 是否提交事务
    :return: 保存的结果，为model的实例列表
    """
    model_instances = []

    for request_body in request_body_list:
        obj_id = request_body.get(primary_key_field, None)
        instance = None

        if obj_id is not None:
            # 根据主键查找已有记录
            instance = session.get(model, obj_id)

        if instance:
            # 更新已有记录，只更新模型中存在的字段
            for key, value in request_body.items():
                if hasattr(model, key) and key != primary_key_field:
                    setattr(instance, key, value)
        else:
            # 构造新增记录
            valid_fields = {key: value for key, value in request_body.items() if hasattr(model, key)}
            instance = model(**valid_fields)
            session.add(instance)

        model_instances.append(instance)

    try:
        if commit:
            session.commit()
    except Exception as e:
        session.rollback()
        setup_logger().error("数据库提交失败:\n%s", traceback.format_exc())
        raise RuntimeError("数据更新失败") from e

    return model_instances


def apply_filters(query, model, filters):
    """
    动态添加搜索条件
    :param query: SQLAlchemy Query对象
    :param model: SQLAlchemy 模型类
    :param filters: 字典形式的搜索条件，key为模型的字段名，value为包含搜索值和查询类型的字典
    {'name': {'value': 'John', 'is_fuzzy': True}} name是字段名，value是搜索值，is_fuzzy是是否模糊查询
    :return: 处理后的查询对象
    """
    if filters:
        filters = json.loads(filters)
        if len(filters) > 0:
            filter_conditions = []
            for key, condition in filters.items():
                value = condition.get('value')
                is_fuzzy = condition.get('is_fuzzy', False)

                # ✅ 只有当 model 中有这个字段时才进行处理
                if hasattr(model, key):
                    if value is not None and value != '':
                        if is_fuzzy:
                            filter_conditions.append(getattr(model, key).like(f'%{value}%'))
                        else:
                            filter_conditions.append(getattr(model, key) == value)

            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
    return query


def get_sorted_query(session, model, sort_by, order):
    """
    根据排序字段和顺序返回排序后的查询对象
    :param session: SQLAlchemy Session对象
    :param model: SQLAlchemy 模型类
    :param sort_by: 排序字段
    :param order: 排序顺序（'asc' 或 'desc'）
    :return: 排序后的查询对象
    """
    if order == 'desc':
        query = session.query(model).order_by(desc(getattr(model, sort_by)))
    elif order == 'asc':
        query = session.query(model).order_by(asc(getattr(model, sort_by)))
    else:
        query = session.query(model)
    return query
