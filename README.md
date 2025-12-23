# Testing full level
python3 IDOR.py -u http://localhost:42001

# Testing level LOW
python3 IDOR.py -u http://localhost:42001 -l low

# Testing level MEDIUM
python3 IDOR.py -u http://localhost:42001 -l medium
