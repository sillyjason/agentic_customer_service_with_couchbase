from couchbaseops import cluster
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchainagents.embedding import create_openai_embeddings
from couchbaseops import insert_doc, flush_collection, run_query
import json
from sharedfunctions.print import print_success

#delete current docs. curently not working so resorting to the more primitive method
# query = '''
#   DELETE FROM `main`.`data`.`policies`
# '''

# try:
#     result = cluster.query(query)
#     print("Deleted current collection")

# except Exception as e:
#     print("exception:", e)



### create indexes 
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`policies` to create a primary index")
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`orders` to create a primary index")
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`products` to create a primary index")
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`messages` to create a primary index")
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`message_responses` to create a primary index")
# run_query("CREATE PRIMARY INDEX ON `default`:`main`.`data`.`refund_tickets` to create a primary index")



### flush all existing collections ###
flush_collection("main", "data", "policies")
flush_collection("main", "data", "orders")
flush_collection("main", "data", "products")
flush_collection("main", "data", "messages")
flush_collection("main", "data", "message_responses")
flush_collection("main", "data", "refund_tickets")



### re-upload products data ###
with open("dataset/products.json") as f:
    data = json.load(f)
    
    for product in data:
        insert_doc("main", "data", "products", product, product["product_id"])
    
    print("Inserted all docs for products")
    

### re-upload order data ###
with open("dataset/orders.json") as f:
    data = json.load(f)
    
    for order in data:
        insert_doc("main", "data", "orders", order, order["order_id"])
    
    print("Inserted all docs for orders")
        



### retrieve policy documents from faq.txt ###
with open("dataset/faq.txt") as f:
    data = f.read()
    

# splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["****"]
)

texts = text_splitter.create_documents([data])

# embed and upload to couchbase
for text in texts:
    # extract text content
    content = text.page_content
    content = content.strip()

    # create embeddings
    embedding = create_openai_embeddings(content) 
    embeddings_dict = {
        "text": content, 
        "embedding": embedding,
        "source": "faq",
        "version": "1.0.0"
    }
    
    # insert into couchbase
    insert_doc("main", "data", "policies", embeddings_dict)

print_success("Inserted all docs")


