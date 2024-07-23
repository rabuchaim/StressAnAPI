#### What's new in v1.0.3 - 22/July/2024

- Found a bug in httpStats that if the server responded with "urlopen error timed out" in some cases it was not being counted correctly, and ONLY WHEN requesting statistics (key `S`) the application crashed. It should appear as error 901, but it appears as "None". Now it is being counted correctly and this problem should not occur anymore. If you notice the same behavior, run the application with the '--debug' option and open an issue providing steps to reproduce the problem. (https://github.com/rabuchaim/StressAnAPI/issues/1)

- The "url" value of the configuration file can now accept template variables:
    - %%randomipv4%% to be replaced by a random IPv4
    - %%randomipv6%% to be replaced by a random IPv6
    - %%randomprivateipv4%% to be replaced by a random Private IPv4
    - %%randomint:val_min:val_max%% to be replaced by a random integer between 'val_min' and 'val_max'
    
    Example: 
```
        {
            "url":"http://127.0.0.1:8000/api/v1/customer/%%randomint:1:10000%%",
            "method":"GET"
        }
        
        or
        
        {
            "url":"http://127.0.0.1:8000/api/v1/testip/%%randomipv4%%",
            "method":"GET"
        }
```

#### What's new in v1.0.2 - 18/July/2024

- Now we have a rounded increment/decrement in the functions decreaseInterval (DOWN key) and increaseInterval (UP key)
- Now we have a rounded increment/decrement in the functions decreaseTimeout (MINUS key) and increaseTimeout (PLUS key)
- Some improvements to the statistics display function
- It is now possible to send everything to a syslog server (including all request responses). To avoid affecting the performance of the stress test, we recommend that you use a LOCAL syslog server and use the UDP protocol.
- Improvement in simple_stressanapi_server.py making it possible to define a CPU core to isolate the process (--cpu)

#### What's new in v1.0.1 - 13/July/2024

- Improvement in memory consumption if you choose to run stressanapi for hours/days. Now it will never exceed 40 MB of RAM.
- Improvement in the simple_stressanapi_server.py. Now you can run by entering the IP and port number using the --host and --port parameters

