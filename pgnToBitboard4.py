import numpy as np
import pandas as pd
import chess
import chess.pgn
import random
import os
import csv

f1 = open('data.csv', 'w', encoding='UTF8', newline='')
w1 = csv.writer(f1)

def pgn2fen(game):
	"""
	Returns array of random sample of positions[FEN] from game[PGN]

	"""
	node = game
	positions = []

	while not node.is_end():
		nextNode = node.variation(0)
		position = nextNode.board().fen()
		positions.append(position)
		node = nextNode
	return positions

def fen2bitboard(fen):
	"""
	Returns bitboard [np array of shape(1, 768)] from fen

	Input:
		fen: A chessboard position[FEN]
	Output:
		bitboard: A chessboard position [bitboard - np array of shape(1, 768)] or None if evaluation is announced mate
		evaluation: A centipawn evaluation from perspective of player with a turn. positive = better negative = worse. None if mate is announced.
	"""
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
	[position, turn, _, _, _, _] = fen.split(' ')
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
	return bitboard, turn

def pgn2bitboard():
	"""
	Iterate over all games of pgnFile and write some good position's bitboard and evaluation to given csv files

	"""
	pgnFile = open('finding-elo/data.pgn')
	game = chess.pgn.read_game(pgnFile)
	evals = pd.read_csv('finding-elo/stockfish.csv')
	i = 0
	while game is not None:
		positions = pgn2fen(game)
		e = evals.loc[i,'MoveScores'].split(' ')
		for x in range(0,len(positions)):
			bitboard, turn = fen2bitboard(positions[x])
			#position evaluated to announced mate. We are choosing to ignore these positions.
			if e[x] != 'NA' and e[x] != '':
				arr = list(bitboard)
				if turn == 'w':
					arr.append(float(e[x]) / 12352)
					w1.writerow(arr)
				else:
					arr.append((-1*float(e[x])) / 12352)
					w1.writerow(arr)
		print('games processed: '+str(i), end='\r')
		i+=1
		game = chess.pgn.read_game(pgnFile)


pgn2bitboard()
print('done')