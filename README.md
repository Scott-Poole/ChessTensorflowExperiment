# ChessTensorflowExperiment

A few files used in a much larger chess playing neural network endevour.

pgnToBitBoard4.py - A script used to sample chess .pgn files and convert information about chess games 
  into data points of a chess position and its respective stockfish chess position evaluation. (The stockfish 
  engine is a dependency not included in this repository). This script writes these data points to csv files that 
  can be used for training a tensorflow model.

neuralNetwork3.py - A script used to import the data points from the csv files created from pgnToBitBoard4.py and
  train a tensorflow model. The hope for the neural network was to take a chess position as input and predict the
  stockfish eninge's evaluation. This script saves the best model at the end of each training epoch to a tensorflow
  .hdf5 file.
  
evaluatemodel.py - A script that could be used with a set of test data and evaluations to conduct tensorflow's 
  evaluate.model() and print the results.
  
app2.py - A part of a larger project file that uses Flask to deploy and interact with the web application index.html.
  This script essentially listens to the html file for played chess moves and then uses a tensorflow model output by
  neuralNetwork3.py to chose a move in response. The move is then sent back to the script in index.html.
  
index.html - A simple GUI that uses chess.js, chessboard.js, and JQuery (needed by chessboard.js, but also needed to send
  JSON objects between this script and app2.py). This chess GUI was adapted from my Sunfish.js project.
