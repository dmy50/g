import socket
from _thread import *
import pickle
from constants import *
import time

server = SERVER_IP
port = PORT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for connections, Server Started")

# Lobby system
players_in_lobby = {}  # {conn: {"name": str, "timestamp": float}}
active_matches = {}    # {match_id: {"p1": conn, "p2": conn, "data": {...}}}
match_counter = 0

def handle_lobby_client(conn, addr):
    """Handle a client in the lobby"""
    try:
        # Receive player name
        player_name = pickle.loads(conn.recv(2048))
        players_in_lobby[conn] = {"name": player_name, "timestamp": time.time()}
        print(f"{player_name} joined the lobby from {addr}")
        
        while conn in players_in_lobby:
            try:
                # Send list of available players
                lobby_list = [info["name"] for c, info in players_in_lobby.items() if c != conn]
                conn.sendall(pickle.dumps({"type": "lobby_list", "players": lobby_list}))
                
                # Receive command
                data = pickle.loads(conn.recv(2048))
                
                if not data:
                    break
                    
                if data.get("type") == "challenge":
                    # Player wants to challenge someone
                    target_name = data.get("target")
                    # Find target conn
                    target_conn = None
                    for c, info in players_in_lobby.items():
                        if info["name"] == target_name:
                            target_conn = c
                            break
                    
                    if target_conn:
                        # Create match
                        global match_counter
                        match_id = match_counter
                        match_counter += 1
                        
                        active_matches[match_id] = {
                            "p1": conn,
                            "p2": target_conn,
                            "p1_pos": (100, SCREEN_HEIGHT // 2),
                            "p2_pos": (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
                        }
                        
                        # Remove from lobby
                        del players_in_lobby[conn]
                        del players_in_lobby[target_conn]
                        
                        # Start match for both
                        conn.sendall(pickle.dumps({"type": "match_start", "match_id": match_id, "player_num": 1}))
                        target_conn.sendall(pickle.dumps({"type": "match_start", "match_id": match_id, "player_num": 2}))
                        
                        # Handle match
                        handle_match(match_id)
                        return
                        
            except:
                break
                
    except Exception as e:
        print(f"Error in lobby: {e}")
    finally:
        if conn in players_in_lobby:
            name = players_in_lobby[conn]["name"]
            del players_in_lobby[conn]
            print(f"{name} left the lobby")
        conn.close()

def handle_match(match_id):
    """Handle an active match"""
    match = active_matches[match_id]
    p1_conn = match["p1"]
    p2_conn = match["p2"]
    
    try:
        while True:
            # Receive positions from both players
            try:
                p1_data = pickle.loads(p1_conn.recv(2048))
                if not p1_data:
                    break
                match["p1_pos"] = p1_data
                
                p2_data = pickle.loads(p2_conn.recv(2048))
                if not p2_data:
                    break
                match["p2_pos"] = p2_data
                
                # Send opponent position to each player
                p1_conn.sendall(pickle.dumps(match["p2_pos"]))
                p2_conn.sendall(pickle.dumps(match["p1_pos"]))
                
            except:
                break
    except Exception as e:
        print(f"Match {match_id} error: {e}")
    finally:
        del active_matches[match_id]
        p1_conn.close()
        p2_conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(handle_lobby_client, (conn, addr))
