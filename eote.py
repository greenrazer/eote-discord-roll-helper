import asyncio
import nest_asyncio # must be before any imports
nest_asyncio.apply()

import json
from functools import partial
import http
import http.server
import socketserver
import os
import sys

import discord


DISCORD_CLIENT_TOKEN_KEY = "discordClientToken"
DISCORD_CHANNEL_ID_KEY = "discordChannelId"
POSSIBLE_PORTS_KEY = "possiblePorts"

TEMP_VARIABLE_L_SP_PAREN = "<<<<<ae05d0454a05221d2705b1e8b3df7997"
TEMP_VARIABLE_R_SP_PAREN = ">>>>>b61d275e529583db4f8f94f82ef96851"

TEMP_VARIABLE_L_PAREN = "<<<<<1c67bbc1e3d67fcb0f99cbe596ddc6bf"
TEMP_VARIABLE_R_PAREN = ">>>>>5adc29d9c262b3b393f1effce07f15d5"

POST_SEPERATOR = "<<|>>"

def quit(message=None):
	if message is None:
		sys.exit()
	else:
  	sys.exit(message)

def fill_template(templ_string, fill_dict):
	temp_main_template = templ_string.replace("{%", TEMP_VARIABLE_L_SP_PAREN)
	temp_main_template = temp_main_template.replace("%}", TEMP_VARIABLE_R_SP_PAREN)

	temp_main_template = temp_main_template.replace("{", TEMP_VARIABLE_L_PAREN)
	temp_main_template = temp_main_template.replace("}", TEMP_VARIABLE_R_PAREN)

	temp_main_template = temp_main_template.replace(TEMP_VARIABLE_L_SP_PAREN, "{")
	temp_main_template = temp_main_template.replace(TEMP_VARIABLE_R_SP_PAREN, "}")

	temp_main_template = temp_main_template.format(**fill_dict)

	temp_main_template = temp_main_template.replace(TEMP_VARIABLE_L_PAREN, "{")
	temp_main_template = temp_main_template.replace(TEMP_VARIABLE_R_PAREN, "}")

	return temp_main_template

def filenames_in_directory(direc):
	for (_, _, filenames) in os.walk(direc):
			return filenames

def build_player_data_json():
	out_arr = []
	for file in filenames_in_directory("saved"):
		if (file != '.gitignore'):
			with open(f"saved/{file}", "r") as f:
				out_arr.append(json.load(f))
	return json.dumps(out_arr)

def get_html():
	with open("templates/main.tmpl", "r") as f:
		main_template = f.read()

	with open("templates/style.css", "r") as f:
		style = f.read()

	with open("default.json", "r") as f:
		default_info = json.load(f)

	player_data = build_player_data_json()

	fill_dict = {
		"style_info":style,
		"default_player_data":json.dumps(default_info),
		"player_data":player_data,
		"post_seperator":POST_SEPERATOR
	}

	return fill_template(main_template, fill_dict)

def create_roll_command(data):
	command = []

	if data["greens"] > 0:
		command.append(f"{data['greens']}g")

	if data["yellows"] > 0:
		command.append(f"{data['yellows']}y")

	if data["blues"] > 0:
		command.append(f"{data['blues']}b")

	if data["purples"] > 0:
		command.append(f"{data['purples']}p")
	
	if data["blacks"] > 0:
		command.append(f"{data['blacks']}k")

	if data["reds"] > 0:
		command.append(f"{data['reds']}r")
	
	if len(command) > 0:
		return "!r " + " ".join(command)
	else:
		return None

def save_json_to_file(data):
	with open(f"saved/{data['base']['name']}.json", "w") as f:
		json.dump(data, f)

def delete_json_file(data):
	os.remove(f"saved/{data['base']['name']}.json")

class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, discord_client, discord_channel_id, *args, **kwargs):
		self.discord_client = discord_client
		self.discord_channel = discord_client.get_channel(discord_channel_id)
		super().__init__(*args, **kwargs)
	
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		html = get_html()
		self.wfile.write(bytes(html, "utf8"))

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length).decode("utf-8")
		if post_data == "shutdown":
			print("Shutting Down")
			quit()
		elif post_data == "destiny":
			self.send_message("!destiny roll")
		else:
			command, data = post_data.split(POST_SEPERATOR)
			json_post_data = json.loads(data)
			if command == "roll":
				roll_command = create_roll_command(json_post_data)
				if roll_command is not None:
					self.send_message(roll_command)
			if command == "save":
				save_json_to_file(json_post_data)

		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.end_headers()

	def send_message(self, message):
		self.discord_client.loop.run_until_complete(self.discord_channel.send(message))

async def serve(discord_client, discord_channel_id, possible_ports):
	handler = partial(HttpRequestHandler, discord_client, discord_channel_id)
	found_port = False
	for p in possible_ports:
		try:
			with socketserver.TCPServer(("", p), handler) as my_server:
				found_port = True
				print(f"starting server on {my_server.server_address[0]}:{my_server.server_address[1]}")
				await discord_client.wait_until_ready()
				await my_server.serve_forever()
				my_server.server_close()
				break
		except OSError:
			print(f"port {p} already in use moving on...")
			continue

	if not found_port:
		print("could not find open port in range")
		quit()

class DiscordClient(discord.Client):
		async def on_ready(self):
			print('Logged on as', self.user)

def main():
	try:
		with open("config.json", "r") as f:
			config = json.load(f)
	except json.decoder.JSONDecodeError:
		quit("'config.json' could not be read, or is not filled in correctly.")

	if all(config[x] is not None for x in [DISCORD_CLIENT_TOKEN_KEY, DISCORD_CHANNEL_ID_KEY]):
		client = DiscordClient()
		client.loop.create_task(serve(client, config[DISCORD_CHANNEL_ID_KEY], config[POSSIBLE_PORTS_KEY]))
		client.run(config[DISCORD_CLIENT_TOKEN_KEY], bot=False)
	else:
		print(f"Could not find {DISCORD_CLIENT_TOKEN_KEY} or {DISCORD_CHANNEL_ID_KEY} in config.json.")
		print("Shutting Down.")
		quit()

if __name__ == "__main__":
	main()