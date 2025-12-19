"""
Repository实现模块

此模块包含所有预定义的Repository类，用户可以直接使用这些类进行数据查询。

推荐使用方式：
    from enn_iot_oc.infrastructure.model import Customer, CustomerRepoImpl
"""

# 从 enn_iot_oc 导入生成的Repository类
from enn_iot_oc.infrastructure.model.Customer import CustomerRepoImpl
from enn_iot_oc.infrastructure.model.CustomerProfile import CustomerProfileRepoImpl
from enn_iot_oc.infrastructure.model.CustomerCategory import CustomerCategoryRepoImpl
from enn_iot_oc.infrastructure.model.ProfileDimension import ProfileDimensionRepoImpl
from enn_iot_oc.infrastructure.model.CategoryRequirement import CategoryRequirementRepoImpl

__all__ = [
    "CustomerRepoImpl",
    "CustomerProfileRepoImpl",
    "CustomerCategoryRepoImpl",
    "ProfileDimensionRepoImpl",
    "CategoryRequirementRepoImpl"
]