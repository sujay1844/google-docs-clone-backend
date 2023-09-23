DELAY_IN_SECS = 1
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import ConnectionManager
import time
import sqlite3

from db import insert_operation, get_all_operations, create_table, reset_table, get_all_operations_since
from transform import transform

current_revision = 0

connection = sqlite3.connect("dev.db")
cursor = connection.cursor()
create_table(cursor, connection)

app = FastAPI()
manager = ConnectionManager()

@app.get("/ping")
async def pong():
	return {"message": "pong"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
	global current_revision
	await manager.connect([client_id, websocket])
	try:
		while True:
			data = await websocket.receive_json()

			if data['revision'] > current_revision:
				current_revision = data['revision']

			time.sleep(DELAY_IN_SECS)
			required_operations = get_all_operations_since(cursor, data['revision'])
			for operation in required_operations:
				data = transform(data, operation)
			
			data['revision'] = current_revision + 1
			print(f"Client {client_id} sent: {data}")
			insert_operation(cursor, connection, data)

			await manager.broadcast(client_id, data)
			await manager.send_acknowledgement(client_id, data)
	except WebSocketDisconnect:
		manager.disconnect([client_id, websocket])

@app.get("/operations")
async def get_operations():
	return get_all_operations(cursor)

@app.get("/reset")
async def reset():
	global current_revision
	reset_table(cursor, connection)
	current_revision = 0
	return {"message": "reset"}