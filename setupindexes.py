from couchbaseops import run_query


# create indexes 
def create_primary_index(bucket_name, scope_name, collection_name):
    run_query(f"CREATE PRIMARY INDEX ON `{bucket_name}`:`{scope_name}`.`{collection_name}`")
    

create_primary_index("main", "data", "policies")
create_primary_index("main", "data", "orders")
create_primary_index("main", "data", "products")
create_primary_index("main", "data", "messages")
create_primary_index("main", "data", "message_responses")
create_primary_index("main", "data", "refund_tickets")