#### What's new in v1.0.2 - 18/July/2024

- Now we have a rounded increment/decrement in the functions decreaseInterval (DOWN key) and increaseInterval (UP key)
- Now we have a rounded increment/decrement in the functions decreaseTimeout (MINUS key) and increaseTimeout (PLUS key)
- Some improvements to the statistics display function
- It is now possible to send everything to a syslog server (including all request responses). To avoid affecting the performance of the stress test, we recommend that you use a LOCAL syslog server and use the UDP protocol.
- Improvement in simple_stressanapi_server.py making it possible to define a CPU core to isolate the process (--cpu)

#### What's new in v1.0.1 - 13/July/2024

- Improvement in memory consumption if you choose to run stressanapi for hours/days. Now it will never exceed 40 MB of RAM.
- Improvement in the simple_stressanapi_server.py. Now you can run by entering the IP and port number using the --host and --port parameters

