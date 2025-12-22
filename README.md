# Testing full level
python3 IDOR.py -u http://localhost:42001

# Testing level LOW
python3 IDOR.py -u http://localhost:42001 -l low

# Testing level MEDIUM
python3 IDOR.py -u http://localhost:42001 -l medium

# Testing level HIGH
python3 IDOR.py -u http://localhost:42001 -l high

# Testing level IMPOSSIBLE
python3 IDOR.py -u http://localhost:42001 -l impossible
