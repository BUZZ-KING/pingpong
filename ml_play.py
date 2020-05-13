"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import math
import numpy as np

def ml_loop(side: str):
	"""
	The main loop for the machine learning process

	The `side` parameter can be used for switch the code for either of both sides,
	so you can write the code for both sides in the same script. Such as:
	```python
	if side == "1P":
		ml_loop_for_1P()
	else:
		ml_loop_for_2P()
	```

	@param side The side which this script is executed for. Either "1P" or "2P".
	"""

	# === Here is the execution order of the loop === #
	# 1. Put the initialization code here

	# 2. Inform the game process that ml process is ready
	comm.ml_ready()
	predict_platX = 75
	predict_ballX = 75

	# 3. Start an endless loop
	if side=='1P':
		Vx = 7
		Vy = -7
		while True:
			# 3.1. Receive the scene information sent from the game process.
			scene_info = comm.recv_from_game()
			# 3.2. If the game is over or passed, the game process will reset
			#      the scene immediately and send the scene information again.
			#      Therefore, receive the reset scene information.
			#      You can do proper actions, when the game is over or passed.
			if scene_info.status == GameStatus.GAME_1P_WIN or \
			   scene_info.status == GameStatus.GAME_2P_WIN:
				# Do something updating or reseting stuff

				# 3.2.1 Inform the game process that
				#       the ml process is ready for the next round
				comm.ml_ready()
				continue		

			# 3.3. Put the code here to handle the scene information
			if scene_info.frame == 0:
				y_direction = 0
				y_last_position = scene_info.ball[1]
				x_direction = 0
				x_last_position = scene_info.ball[0]
				x_last_direction = 0
				x_rebound = 0
				y_rebound = 0

			else:
				Vy = scene_info.ball_speed
				Vx = scene_info.ball_speed
				distance = lambda x: 1 if x > 0 else -1
				y_direction = distance(scene_info.ball[1] - y_last_position)
				x_direction = distance(scene_info.ball[0] - x_last_position)
				if scene_info.ball[0] - x_last_position != Vx:
					x_rebound = 1
					Vx = -Vx
				else:
					x_rebound = 0
				if scene_info.ball[1] - y_last_position != Vy:
					y_rebound = 1
					Vy = -Vy
				else:
					y_rebound = 0
			# if y_direction == 1:
			# 	x_rebound = 0
			# if scene_info.ball[1] > 280:
			# 	y_rebound = 0


			# My rule for predict position	
			if y_rebound != 0:
				x_temp = scene_info.ball[0]
				y_temp = scene_info.ball[1]
				if Vy < 0:
					times = (int)(math.ceil((y_temp - 80) / abs(Vy)))
					predict_ballx = x_temp + times * Vx
					if predict_ballx < 0:
						times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
						predict_ballx = abs(Vx) * times
					if predict_ballx > 195:
						times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
						predict_ballx = 195 - abs(Vx) * times
					predict_platX = predict_ballx - 17
				else:
					times = (int)(math.ceil((415 - y_temp) / abs(Vy)))
					predict_ballx = x_temp + times * Vx
					if predict_ballx < 0:
						times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
						predict_ballx = abs(Vx) * times
					if predict_ballx > 195:
						times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
						predict_ballx = 195 - abs(Vx) * times
					times = (int)(math.ceil((415 - 80) / abs(Vy)))
					predict_ballx = predict_ballx + times * Vx
					if predict_ballx < 0:
						times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
						predict_ballx = abs(Vx) * times
					if predict_ballx > 195:
						times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
						predict_ballx = 195 - abs(Vx) * times	


			if x_rebound != 0:
				x_temp = scene_info.ball[0]
				y_temp = scene_info.ball[1]
				times = (int)(math.ceil((y_temp - 80) / abs(Vx)))
				predict_ballx = x_temp + times * Vx
				if predict_ballx < 0:
					times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
					predict_ballx = abs(Vx) * times
				if predict_ballx > 195:
					times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
					predict_ballx = 195 - abs(Vx) * times
			# 	predict_platX = predict_ballx - 17
			# 	print(predict_platX)
			# print([scene_info.ball[0], scene_info.ball[1]])
			# print(input_current)
			# 3.4. Send the instruction for this frame to the game process
			# if scene_info.ball[1] > 280 or y_direction == 1:
			# 	if scene_info.platform_1P[0] > 75:
			# 		instruct = -1
			# 		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
			# 	elif scene_info.platform_1P[0] < 75:
			# 		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
			# 		instruct = 1
			# 	else:
			# 		comm.send_instruction(scene_info.frame, PlatformAction.NONE)
			# 		instruct = 0
			# else:
			if scene_info.platform_1P[0] > predict_platX:
				comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
				instruct = -1
			elif scene_info.platform_1P[0] < predict_platX:
				comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
				instruct = 1
			else:
				comm.send_instruction(scene_info.frame, PlatformAction.NONE)

			x_last_position = scene_info.ball[0]
			y_last_position = scene_info.ball[1]
			x_last_direction = x_direction
	else:
		Vx = 7
		Vy = 7
		while True:
			# 3.1. Receive the scene information sent from the game process.
			scene_info = comm.get_scene_info()

			# 3.2. If the game is over or passed, the game process will reset
			#      the scene immediately and send the scene information again.
			#      Therefore, receive the reset scene information.
			#      You can do proper actions, when the game is over or passed.
			if scene_info.status == GameStatus.GAME_1P_WIN or \
			   scene_info.status == GameStatus.GAME_2P_WIN:
				# Do something updating or reseting stuff

				# 3.2.1 Inform the game process that
				#       the ml process is ready for the next round
				comm.ml_ready()
				continue		

			# 3.3. Put the code here to handle the scene information
			if scene_info.frame == 0:
				y_direction = 0
				y_last_position = scene_info.ball[1]
				x_direction = 0
				x_last_position = scene_info.ball[0]
				x_last_direction = 0
				x_rebound = 0
				y_rebound = 0

			else:
				Vy = scene_info.ball_speed
				Vx = scene_info.ball_speed
				distance = lambda x: 1 if x > 0 else -1
				y_direction = distance(scene_info.ball[1] - y_last_position)
				x_direction = distance(scene_info.ball[0] - x_last_position)
				if scene_info.ball[0] - x_last_position != Vx:
					x_rebound = 1
					Vx = -Vx
				else:
					x_rebound = 0
				if scene_info.ball[1] - y_last_position != Vy:
					y_rebound = 1
					Vy = -Vy
				else:
					y_rebound = 0
			# if y_direction == -1:
			# 	x_rebound = 0
			# if scene_info.ball[1] < 200:
			# 	y_rebound = 0


			# My rule for predict position	
			if y_rebound != 0:
				x_temp = scene_info.ball[0]
				y_temp = scene_info.ball[1]
				times = (int)(math.ceil((415 - y_temp) / abs(Vx)))
				predict_ballx = x_temp + times * Vx
				if predict_ballx < 0:
					times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
					predict_ballx = abs(Vx) * times
				if predict_ballx > 195:
					times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
					predict_ballx = 195 - abs(Vx) * times
				predict_platX = predict_ballx - 17
				# print('Predict ball: ', predict_ballx)
				# print(y_direction)


			if x_rebound != 0:
				x_temp = scene_info.ball[0]
				y_temp = scene_info.ball[1]
				times = (int)(math.ceil((415 - y_temp) / abs(Vx)))
				predict_ballx = x_temp + times * Vx
				if predict_ballx < 0:
					times = (int)(math.floor((0 - predict_ballx) / abs(Vx)))
					predict_ballx = abs(Vx) * times
				if predict_ballx > 195:
					times = (int)(math.floor((predict_ballx - 195) / abs(Vx)))
					predict_ballx = 195 - abs(Vx) * times
				predict_platX = predict_ballx - 17
			# print([scene_info.ball[0], scene_info.ball[1]])
			# print(predict_platX)
			# print(input_current)
			# 3.4. Send the instruction for this frame to the game process
			# if scene_info.ball[1] < 200 or y_direction == -1:
			# 	if scene_info.platform_2P[0] > 75:
			# 		instruct = -1
			# 		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
			# 	elif scene_info.platform_2P[0] < 75:
			# 		comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
			# 		instruct = 1
			# 	else:
			# 		comm.send_instruction(scene_info.frame, PlatformAction.NONE)
			# 		instruct = 0
			# else:
			if scene_info.platform_2P[0] > predict_platX:
				comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
				instruct = -1
			elif scene_info.platform_2P[0] < predict_platX:
				comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
				instruct = 1
			else:
				comm.send_instruction(scene_info.frame, PlatformAction.NONE)

			x_last_position = scene_info.ball[0]
			y_last_position = scene_info.ball[1]
			x_last_direction = x_direction
