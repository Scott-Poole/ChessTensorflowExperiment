from flask import Flask, render_template, jsonify
import chess
import random
import tensorflow as tf
from tensorflow import keras
import numpy as np
import chess.polyglot

board = chess.Board()

chess_model = tf.keras.models.load_model('best_model.hdf5')

reader = chess.polyglot.open_reader("gm2001.bin")

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/resetGame/<string:color>')
def resetGame(color):
	board.reset()
	if color == 'b':
		playMove()
	
	return board.fen()

@app.route('/tryMove/<string:source>/<string:target>/<string:promotion>')
def tryMove(source, target, promotion):
	
	move = chess.Move(chess.parse_square(source), chess.parse_square(target))
	promoteMove = chess.Move(chess.parse_square(source), chess.parse_square(target), chess.Piece.from_symbol(promotion).piece_type)
	
	if move in board.legal_moves:
		board.push(move)
	elif promoteMove in board.legal_moves:
		board.push(promoteMove)
	else:
		return jsonify(
				fen=board.fen(),
			)
	if board.is_game_over():
		print(str(board.outcome().termination))
		return jsonify(
			fen=board.fen(),
			result=board.outcome().result(),
			termination=str(board.outcome().termination)
		)
	
	playMove()
	
	if board.is_game_over():
		return jsonify(
			fen=board.fen(),
			result=board.outcome().result(),
			termination=str(board.outcome().termination)
		)
	
	return jsonify(
			fen=board.fen(),
		)
	
def playMove():
	# try to follow book opening
	try:
		entry = reader.weighted_choice(board)
		print('book move')
		board.push(entry.move)
	# out of book play
	except IndexError:
	# search for best move
		be, bm = search(chess.Board(board.fen()),2)
		print('rand or ai move')
		print(be)
	# play ai move or random move if all moves lead to draw
		board.push(bm)


def search(b, d):
	bestMove = None
	bestEval = 1
	for move in b.legal_moves:
		b.push(move)
		if d > 1:
			e,m = search(chess.Board(b.fen()),d-1)
			e*=-1
		else:
			e = chess_model.predict(getBitboard(b))
		if e < bestEval:
			bestEval = e
			bestMove = move
		b.pop()
	return bestEval, bestMove

def isMateIn(b, d):
	for move in b.legal_moves:
		b.push(move)
		if b.is_checkmate():
			return True, move
		if d > 1 and isForcedMateIn(chess.Board(b.fen()),d):
			return True, move
		b.pop()	
	return False, None

def isForcedMateIn(b,d):
	for move in b.legal_moves:
		b.push(move)
		isM, m = isMateIn(chess.Board(b.fen()), d-1)
		if not isM:
			return False
		b.pop()
	return True
	
def getBitboard(b):
	mapping = {
		'P': 0,
		'N': 1,
		'B': 2,
		'R': 3,
		'Q': 4,
		'K': 5,
		'p': 6,
		'n': 7,
		'b': 8,
		'r': 9,
		'q': 10,
		'k': 11
	}
	bitboard = np.zeros(768, dtype=int)
	col = 0
	row = 7
	[position, turn, _, _, _, _] = b.fen().split(' ')
	for ch in position:
		if ch == '/':
			row -= 1
			col = 0
			continue
		elif ch >= '1' and ch <= '8':
			col += (ord(ch) - ord('0'))
		else:
			if (turn == 'w' and mapping[ch] < 6) or (turn == 'b' and mapping[ch] > 5):
				bitboard[mapping[ch]*64 + row*8 + col] = 1
			else:
				bitboard[mapping[ch]*64 + row*8 + col] = -1
			col += 1
	return np.reshape(bitboard, (1,768))
	
if __name__ == '__main__':
	app.run(debug=True, port=5000)