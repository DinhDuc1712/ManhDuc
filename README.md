# Testing full level
python3 IDOR.py -u http://localhost:8000

# Testing level LOW
python3 IDOR.py -u http://localhost:8000 -l low

# Testing level MEDIUM
python3 IDOR.py -u http://localhost:8000 -l medium
