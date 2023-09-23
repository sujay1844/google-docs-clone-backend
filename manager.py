from fastapi import WebSocket

class ConnectionManager:
	def __init__(self):
		self.connections: list[list[int, WebSocket]] = []

	async def connect(self, connection: list[int, WebSocket]):
		await connection[1].accept()
		self.connections.append(connection)
	
	def disconnect(self, connection: list[int, WebSocket]):
		self.connections.remove(connection)
	
	async def broadcast(self, client_id: int, data: dict):
		for client_id_idx, websocket in self.connections:
			if client_id != client_id_idx:
				await websocket.send_json({
					"ack": False,
					"change": data
				})
	
	async def send_acknowledgement(self, client_id: int, data: dict):
		for connection in self.connections:
			if connection[0] == client_id:
				await connection[1].send_json({
					"ack": True,
					"change": data
				})
				break