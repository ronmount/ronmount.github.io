# -*- coding: utf-8 -*-

# Версия бота: 1.0.3
# Создатель скрипта: vk.com/0id000000

import re

from requests import exceptions
from requests import get
from requests import post

from os import path
from mcrcon import MCRcon
from datetime import datetime
from threading import Thread
from time import sleep
from ruamel.yaml import YAML


class Api:

	def __init__(self, token, group):
		self.token = token
		self.group = group
		self.apiurl = 'https://api.vk.com/method/'

	'''получаем данные для подключения к longpoll серверу'''
	def get_lps(self):
		params = {'access_token': self.token,
				  'group_id': self.group,
				  'v': '5.87'}
		
		return self.method('groups.getLongPollServer', params)

	'''получаем все события от longpoll сервера'''
	def get_events(self):
		
		lps = self.get_lps()

		params = {'act': 'a_check',
				  'key': lps['key'],
				  'ts': lps['ts'],
				  'wait': 90,
				  'mode': 2,
				  'version': 2}

		r = get(lps['server'], params=params).json()

		if 'failed' not in r:
			return r['updates']
		else:
			print(r)

	'''отправка сообщения в нужный диалог'''
	def write(self, peer_id, text='Write test'):

		params = {'peer_id': peer_id,
				  'message': str(text),
				  'group_id': self.group,
		   		  'access_token': self.token,
				  'v': '5.87'}

		return self.method('messages.send', params=params)

	'''выполнение метода vkapi'''
	def method(self, method: str, params):
		if params.get('access_token') is None:
			params.update({'access_token': self.token})
		
		request = get(self.apiurl + method, params=params).json()

		if 'error' not in request:
			return request['response']
		else:
			print('[ERROR]: Ошибка при выполнении метода: {m}'.format(m=method))
			print(request)
			return request

class Rcon():
	def __init__(self, host, password, port):
		self.host = host
		self.password = password
		self.port = port

		self.mcr = MCRcon(host = self.host,
						  password = self.password,
						  port = self.port)
		self.mcr.connect()
	
	def send(self, cmd):
		return self.mcr.command(cmd)


class Config:
	def __init__(self, file='config.yml'):
		self.yaml = YAML(typ='unsafe', pure=True)
		self.yaml.allow_unicode = True
		self.yaml.default_flow_style = False
		self.file = file

	def load(self):
		if path.exists(self.file):
			with open(self.file, encoding='utf-8-sig') as load_file:
				print('[INFO]: Данные конфига загружены!!')
				return self.yaml.load(load_file)
		else:
			print('[WARN]: Файл конфига не обнаружен!\n[INFO]: Создаем конфиг..')
			
			default_cfg = {
			 'api': {
			 	'token': 'Токен сообщества',
			 	'group_id': 'id сообщества',
			 	},
			 'cmd': 'rcon',
			 'rcon': {
			 	'host': '127.0.0.1',
			 	'port': 25577,
			 	'password': 'superSecret' 
			 	},
			 'send-response': {
			 	'enable': 1
			 	},
			 'messages': {
			 	'rcon-empty-response': 'Пустой ответ RCON сервера!',
			 	'command-is-blacklisted': 'Эту команду нельзя использовать.',
				'not-in-white-list': 'Вы не можете использовать команду {cmd}'
				},
			 'white-list-ids': [
			 	100
			 	],
			 'black-list-commands': [
			 	'op',
			 	'deop',
			 	'stop',
			 	'reload'
			 	]
			 }
			with open(self.file, 'w', encoding='utf-8-sig') as outfile:
				self.yaml.dump(default_cfg, outfile)
			
			#self.add_comment()

			print('[INFO]: Конфиг создан. ' + self.file)
			print('[INFO]: Для дальнейшей работы скрипта настрой его!')

			input()
			exit()

class Bot:
	def __init__(self):
		self.cfg = Config().load()

		self.vk_token = self.cfg['api']['token']
		self.vk_group = self.cfg['api']['group_id']

		self.api = Api(self.vk_token, self.vk_group)

		self.rcon_cmd = self.cfg['cmd']

		self.rcon_host = self.cfg['rcon']['host']
		self.rcon_port = self.cfg['rcon']['port']
		self.rcon_password = self.cfg['rcon']['password']

		self.send_response = self.cfg['send-response']['enable']

		self.message_rcon_empty_response = self.cfg['messages']['rcon-empty-response']
		self.message_cmd_is_blacklist = self.cfg['messages']['command-is-blacklisted']
		self.message_user_not_in_whitelist = self.cfg['messages']['not-in-white-list']

		self.white_list_ids = self.cfg['white-list-ids']
		self.black_list_cmds = self.cfg['black-list-commands']

	# Обработка сообщения
	def read_msg(self, msg_data):
		msg_text = msg_data['text']
		msg_date = datetime.fromtimestamp(msg_data['date']).strftime('%H:%M:%S')  # %Y-%m-%d %H:%M:%S
		peer_id = int(msg_data['peer_id'])
		msg_id = msg_data['id']
		from_id = msg_data['from_id']

		if from_id != peer_id:     #сообщение от беседы
			msg_type = 'chat'
			peer_id - 2000000000
		elif from_id == peer_id:   #сообщение от профиля
			msg_type = 'ls'
			peer_id = peer_id

		# Очистка сообщения от упомянаний! (msg_no_citation)
		msg_text = re.sub('\[club.*\] ', '', msg_text)

		if msg_text.lower().startswith(self.rcon_cmd.lower() + ' '):
			
			# Проверяем написавшего боту сообщение пользователя
			# На предмет его нахождения в белом списке юзеров
			if (
				int( from_id ) not in self.white_list_ids
				):
				# Отправляем пользователю оповещение о том что пользоватся rcon он не может
				self.api.write(peer_id, self.message_user_not_in_whitelist.format(cmd=self.rcon_cmd) )
				return

			# Извлекаем текст команды из сообщения
			rcon_send = msg_text[len(self.rcon_cmd) + 1:]

			# Проверяем вводимую команду
			# На её наличие в черном списке команд
			for i in self.black_list_cmds:
				if (
				    rcon_send.lower().startswith(i.lower())
				    ):
					# Отправляем сообщение, что команда находится в черном списке
					self.api.write(peer_id, self.message_cmd_is_blacklist)
					return

			# Подключение к minecraft Rcon
			rcon = Rcon(self.rcon_host,
						self.rcon_password,
						self.rcon_port)

			# Отправляем команду на сервер
			resp = rcon.send(rcon_send)

			if (resp is None or
			    resp == ''):
				resp = self.message_rcon_empty_response

			if bool( self.send_response ):
				# Очистка ответа rcon от цветовых кодов майнкрафт
				resp = re.sub('§.', '', resp)

				self.api.write(peer_id, resp)

		
		
	def check_events(self, events):
		for ev in events:
			if ev['type'] == 'message_new':
				thre = Thread(target = self.read_msg, args = [ev['object']])
				thre.start()
	
	def start(self):

		while True:
			try:
				events = self.api.get_events()
				t = Thread(target = self.check_events, args = [events])
				t.start()
			except exceptions.ConnectionError:
				print('[ERROR]: Ошибка подключения к сети.')
				print('[INFO]: Пробуем подключиться снова через 5 секунд.')
				sleep(5)


if __name__ == '__main__':
	bot = Bot()
	bot.start()