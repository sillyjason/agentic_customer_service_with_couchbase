from pydantic import BaseModel, Field
from typing import List, Optional


class ProductId(BaseModel):
    """the identifier of the product"""
    product_id: str = Field(description="identifier of the product")

class OrdertId(BaseModel):
    """the identifier of the order"""
    order_id: str = Field(description="identifier of the order")


class ProductIDs(BaseModel):
    """A list of product IDs"""
    product_ids: List[ProductId] = Field(description="List of products to be searched in the database")


class Product(BaseModel):
    """The information of the product"""
    product_name: str = Field(description="name of the product")
    product_desc: str = Field(description="description of the product")
    product_warranty: int = Field(description="warranty of the product, in days")


class ProductCategory(BaseModel):
    """The category of products sold"""
    product_category: str = Field(description="category of the product. Either `vacuum` or `wash_machine`")
    
    
class RefundIncident(BaseModel):
    """The refund incident created to address customer's refund request"""
    order_id: str = Field(description="the ID of the sales order associated with the refund request")
    message_id: str = Field(description="the ID of the customer message associated with the refund request")
    refund_reason: str = Field(description="the reason for the refund")
    customer_message: str = Field(description="the message sent by the customer")
    refund_status: str = Field(description="the status of the refund request. Always starts with `pending`")
    
    
class RefundDigest(BaseModel): 
    """The digest of the refund applicability situation for the refund request by customer"""
    product_id: str = Field(description="the id of the product mentioned")
    order_id: str = Field(description="the id of the order mentioned")
    order_date: str = Field(description="the date of the order")
    policy: str = Field(description="the refund policy for the product")
    refund_amount: int = Field(description="the amount to be refunded")
    refund_applicable: bool = Field(description="whether the refund is applicable for the product and order mentioned")


class RefundSinglePolicy(BaseModel): 
    """A single refund policy that consists of 2 parameters: Number-of-days-passed and refund_percentage"""
    days_passed: int = Field(description="the number of days passed since the order was placed")
    refund_percentage: int = Field(description="the percentage of the refund to be made")


class RefundPolicies(BaseModel):
    """A list of refund policies for a product"""
    refund_policies: List[RefundSinglePolicy] = Field(description="List of refund policies for the product")


class RefundEligibilityMaths(BaseModel):
    """The inputs necessary to calculate a refund eligibility"""
    refund_policies: List[RefundSinglePolicy] = Field(description="the refund policies for the product")
    order_date: str = Field(description="the date the order was placed")


class GeneralSupportOutput(BaseModel):
    """The general information abstracted from the customer message and database"""
    draft: str = Field("the drafted message from the support expert")
    product_id: Optional[str] = Field(default=None, description="the id of the product mentioned")
    order_id: Optional[str] = Field(default=None, description="the id of the order mentioned")