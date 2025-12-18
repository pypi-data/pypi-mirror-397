"""
Repository工厂函数
用于创建指定数据源的Repository实例
"""

import os
from typing import Optional
from .customer_repo import CustomerRepoImpl
from ..model.CategoryRequirement import CategoryRequirementRepoImpl

def create_repository_with_sdk_data():
    """
    创建使用SDK包内数据的Repository实例
    这是推荐的默认用法，确保数据一致性
    """
    try:
        import ioc_data_sdk
        sdk_data_dir = os.path.join(os.path.dirname(ioc_data_sdk.__file__), 'data', 'source')

        # 为每个模型创建指定数据源的Repository
        customer_repo = CustomerRepoImpl(data_source_path=os.path.join(sdk_data_dir, 'customer.json'))
        cat_req_repo = CategoryRequirementRepoImpl(data_source_path=os.path.join(sdk_data_dir, 'category_requirement.json'))

        return {
            'customer': customer_repo,
            'category_requirement': cat_req_repo
        }
    except ImportError:
        raise ImportError("SDK数据包未安装，无法创建基于SDK数据的Repository")