Network Vulnerability Scanner: Create a custom scanner (in Python or C++) that uses libraries like
Nmap or raw sockets to probe a network for open ports and known flaws. A vulnerability scanner
gives “a prioritized list of cybersecurity flaws” and helps managers “implement the appropriate
preventative measures” . You could start with a simple host/port scanner and extend it to check
for specific CVEs (for example by integrating a vulnerability database). To make it unique,
containerize your scanner with Docker for easy deployment and add a web dashboard showing
results. (Helps you learn about CVEs, networking, and Linux scripting.)
