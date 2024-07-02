from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import datetime
from couchbaseops import insert_doc, run_query, mutliple_subdoc_upsert, mutliple_subdoc_upsert
from langchainagents.metadata_tag import tag_metadata
from langchainsetup import run_agent_langgraph


load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(msg_to_process):
    print(f'message: {msg_to_process}')
    
    # insert into message collection 
    doc_to_insert = msg_to_process
    doc_to_insert["source"] = "web"
    doc_to_insert["time"] = datetime.datetime.now().isoformat()
    message_id = insert_doc("main", "data", "messages", doc_to_insert)

    # run agent 
    response, run_id, run_url = run_agent_langgraph(msg_to_process['message'])
    final_reply = response['final_response']
    
    print(f'aaa, run_id: {run_id}, run_url: {run_url}, final_reply: {final_reply}')
    run_id = str(run_id)
    
    # insert into message_response collection
    message_response_doc = {
        "message_id": message_id,
        "response": final_reply,
        "time_iso": datetime.datetime.now().isoformat(),  
        "time": datetime.datetime.now().timestamp(),
        "run_id": run_id,
        "run_url": run_url
    }
    
    message_response_id = insert_doc("main", "data", "message_responses", message_response_doc)
    
    # update message doc
    mutliple_subdoc_upsert("main", "data", "messages", message_id, {
        "responded": True,
        "response_id": message_response_id,
        "run_id": run_id
    })
    
    # emit response to client
    socketio.emit("response", {
        "message": final_reply,
        "run_id": run_id,
        "run_url": run_url
    })
    

# @app.route('/run_agents', methods=['POST'])
# def run_agents():
#     data = request.get_json()
#     content = data["content"]
#     message_id = data["message_id"]
#     reply = run_agent(content, message_id)
#     return jsonify({"response": reply})


@app.route('/metadata_tag', methods=['POST'])
def metadata_tag():
    data = request.get_json()
    message = data.get('message', '')
   
    type = tag_metadata(message)

    return jsonify(type)


@app.route('/receive_reply', methods=['POST'])
def receive_reply():
    data = request.get_json()
    message = data.get('message', '')
    
    socketio.emit("response", {
        "message": message
    })
    
    return { "status": "success" }


@app.route('/new_refund_ticket_notification', methods=['POST'])
def new_refund_ticket_notification():
    print('new_refund_ticket_notification')
    
    socketio.emit("new_refund_ticket_creation")
    
    return { "status": "success" }


@app.route('/tickets')
def tickets():
    return render_template('tickets.html')


@app.route('/messages')
def messages():
    return render_template('messages.html')


@socketio.on('init_messages')
def init_messages():
    query = """
        SELECT * 
        FROM `main`.`data`.`messages`
        ORDER BY time DESC
    """
    result = run_query(query)
    
    results = []
    for row in result: 
        print('found row')
        results.append(row)
        emit('new_messages', results)
    
    return 


@socketio.on('init_refund_tickets')
def init_refund_tickets():
    query = """
        SELECT meta() as metadata, * 
        FROM `main`.`data`.`refund_tickets`
        ORDER BY time DESC
    """
    result = run_query(query)
    
    results = []
    for row in result: 
        print('found row')
        results.append(row)
        emit('new_tickets', results)
    
    return 


@socketio.on('approve_refund_ticket')
def approve_refund_ticket(data):

    print("approve_refund_ticket: ", data)
    refund_amount = data.get('refund_amount')
    refund_ticket_id = data.get('refund_ticket_id')
    
    mutliple_subdoc_upsert("main", "data", "refund_tickets", refund_ticket_id, {
        'refund_amount': refund_amount,
        'approved': True
    })
    
    return 


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
    