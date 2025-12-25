<h1>Tool Automate exploit Vulnerabilities on DVWA>Eh1>
<h4># Testing full level </h4>
python3 IDOR.py -u http://localhost:42001

<h4># Testing level LOW </h4>
python3 IDOR.py -u http://localhost:42001 -l low

<h4># Testing level MEDIUM </h4>
python3 IDOR.py -u http://localhost:42001 -l medium

<h4># Testing level LOW CSRF</h4>
python3 CSRF.py http://localhost:4200
