from langchain.tools import tool
from langchainagents.classes import ProductIDs, OrdertId, ProductCategory, RefundIncident, RefundEligibilityMaths
from couchbaseops import get_doc, cluster, cb_vector_search, insert_doc, subdocument_insert
from langchainagents.embedding import create_openai_embeddings
import datetime
from dateutil import parser

@tool(args_schema=OrdertId)
def retrieve_order_info(order_id: str) -> dict:
    """retrieve the information of the order provided"""

    doc = get_doc("main", "data", "orders", order_id)
    
    return doc 


@tool(args_schema=ProductIDs)
def get_product_details(product_ids: list) -> dict:
    """retrieve the information of the order provided from the database"""
    
    # for each product id, retrieve the product details from couchbase using the get_doc function
    product_details = []
    for product_id in product_ids:
        doc = get_doc("main", "data", "products", product_id.product_id)
        product_details.append(doc)
        
    return product_details


@tool(args_schema=RefundIncident)
def create_refund_ticket(order_id: str, refund_reason: str, message_id: str, customer_message: str, refund_status: str) -> dict:
    """create a refund ticket in the database to process customer's valid refund request"""
    
    # insert the refund ticket to the database    
    try:
        ticket_id = f"refund_{order_id}"
        
        ticket_data = {
            "order_id": order_id,
            "approved": False,
            "refund_amount": 0,
            "refund_reason": refund_reason,
            "message_id": message_id,
            "refund_status": refund_status,
            "customer_message": customer_message,
            "time": datetime.datetime.now().isoformat()
        }
        
        insert_doc("main", "data", "refund_tickets", ticket_data, ticket_id)
        
        subdocument_insert("main", "data", "orders", order_id, "refund_ticket_id", ticket_id)
        subdocument_insert("main", "data", "messages", message_id, "refund_ticket_id", ticket_id)
        
        
    except Exception as e:
        # LangChain AgentExecutor somehow restart the chain, no solution is found. So using insert ops
        # to stop the recreation. The error here is intended.
        print("exception:", e)
        
    return {
            "refund_ticket_id": ticket_id,
            "refund_ticket_creation_success": True  
        }


@tool(args_schema=ProductCategory)
def get_category_products(product_category: str) -> list:
    """retrieve the product information in this category for recommendation back to customer"""
    
    result = cluster.query(
    f"""
        select * 
        from `main`.`data`.`products` 
        where category == "{product_category}"
        limit 3
    """
    )

    # iterate over rows
    returned_rows = []
    for row in result:
        # each row is an instance of the query call
        try:
            returned_rows.append(row)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
    return returned_rows



@tool
def get_policies(input: str) -> str: 
    """retrieve the relevant policies for FAQ for the queries asked"""

    embedding = create_openai_embeddings(input)

    result = cb_vector_search("main", "data", "data_fts", "embedding", embedding, ["text"])
    
    # parsing the results
    additional_context = "\n".join([row.fields['text'] for row in result.rows() if 'text' in row.fields and row.fields['text'] is not None])
    
    # remove all empty spaces and line breaks or "\n" characters in the additional context
    additional_context = additional_context.replace("\n", "")
    
    return additional_context


@tool(args_schema=RefundEligibilityMaths)
def calculate_refund_eligibility(refund_policies: list, order_date: str) -> dict:
    """calculate the refund eligibility based on the refund policies and order date provided"""
    
    refund_information = {
        "refund_applicable": False,
        "refund_percentage": 0,
        "refund_policies": [policy.dict() for policy in refund_policies],
        "days_since_purchase": 0,
    }
    
    # if refund_policies is empty array, return false 
    if not refund_policies:
        return refund_information
    
    #turn the order_date field, which is a str, into a datetime obj
    date_obj = parser.parse(order_date)
    
    today = datetime.datetime.now()
    
    # Calculate the difference
    difference = today - date_obj
    diff_in_days = difference.days 
    
    refund_information["days_since_purchase"] = diff_in_days
    
    # find the right policy 
    final_refund_percent = 0 
    
    for policy in refund_policies:
        days = policy.days_passed
        refund_percentage = policy.refund_percentage
        
        # update final_refund_percent to refund_percentage only if days is larger than diff_in_days and that refund_percentage is greater than final_refund_percent
        if days >= diff_in_days and refund_percentage > final_refund_percent:
            final_refund_percent = refund_percentage
            refund_information['refund_applicable'] = True
    
    refund_information["refund_percentage"] = final_refund_percent
    
    return refund_information

        
    
    
    
    