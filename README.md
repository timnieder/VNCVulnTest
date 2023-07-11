# VNC Vulnerability Testing
Written as part of my master thesis.

Contains a VNC client and server implementation to test different VNC implementations for security vulnerabilities.
All found vulnerabilities were responsibly disclosed to the developers and fixed.

## Project Stucture
- client.py: Contains the VNC client implementation
- server.py: Contains the VNC server implementation
- clientTest.py: Starts the VNC server tests contained in clientTests.py and clientAuthBypassTests.py
- clientTestExt.py: Starts the VNC server tests (focused on extensions) contained in clientTestsExt.py
- serverTest.py: Starts the VNC client tests contained in serverTests.py
- serverTestExt.py: Starts the VNC client tests (focused on extensions) contained in serverTestsExt.py

Proof-of-concepts:
- fileTransferServer.py: UltraVNC Client FileTransfer extension tests
- serverUltraVNCCrash.py: UltraVNC Client Buffer Overflow
- serverUltraVNCCrash2.py: UltraVNC Client Denial-of-Service