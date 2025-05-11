# Screenshot & Loop Systems Integration

This project integrates two systems:

1. **Loop system (loop.py)**: Continuously runs the CivRealm agent, automatically restarting the game after each match.
2. **Screenshot system**: Takes automatic screenshots of the game state at regular intervals.

## How it works

### Automatic port detection

- The system now automatically detects the actual port used by the game in the log messages
- When it detects messages like "Reset with port: 6310" or "Log in to port 6310", it updates the .env file
- Detection happens in real-time during program execution

### Non-blocking processing

- Uses **separate threads** to process game output without interfering with its execution
- Allows the game to progress from the preparation phase (pregame) to the actual match
- Monitors log messages in the background to detect port changes

### Delayed start

- The screenshot system starts **3 minutes after** the first execution of `main.py` begins
- This ensures that the agent is already running and the port is active when screenshots are taken

### Dynamic port system

The system is designed to handle changes in the FreeCiv port:

- The port is detected directly from the game logs during execution
- `loop.py` updates the `.env` file with the detected actual port
- The screenshot system continuously monitors changes in the `.env` file
- When it detects a port change, it automatically updates the screenshot URL

### Configuration

You can configure different aspects of the screenshot system by modifying these environment variables:

- `FREECIV_PORT`: FreeCiv port (default: 6302, but updates automatically)
- `SCREENSHOT_SAVE_DIR`: Directory where screenshots are saved (default: "screenshots" folder in the root directory)
- `SCREENSHOT_INTERVAL`: Interval between screenshots in seconds (default: 300 = 5 minutes)
- `SCREENSHOT_WINDOW_SIZE`: Screenshot resolution (default: "1920,1080")

### Execution

To start the entire system, simply run:

```
python loop.py
```

This will start the main agent loop and, after 3 minutes, the automatic screenshot system.

### Testing

To test port changes without waiting for them to occur naturally:

```
python test_port_change.py
```

This script simulates a port change in the `.env` file to verify that the screenshot system can detect it.

## Diagnostics

If the screenshot system does not start correctly:

1. Verify that the `screenshot-capture-system` directory is correctly installed
2. Make sure all dependencies are installed: `pip install -r screenshot-capture-system/requirements.txt`
3. Check access permissions to the directory where screenshots are saved
4. Review the logs to make sure the port is being detected correctly

## Common troubleshooting

- **Game stuck in "pregame" mode**: This issue has been fixed with the implementation of non-blocking threads. If it persists, restart the entire system.
- **Screenshots taken with incorrect port**: The system now automatically detects the port in the logs. If it continues using an incorrect port, verify that the log messages contain the correct format like "Reset with port: XXXX" or "Log in to port XXXX".
- **The .env file is not updating**: Check write permissions in the project folder.
- **Screenshots are not being saved**: Make sure the screenshot directory exists and has write permissions.

## Recent changes

The system has been improved to:

1. **Avoid blocking game execution**:
   - Implementation of separate threads to monitor output without blocking the main process
   - Better management of inter-process communication

2. **Improve port detection**:
   - Real-time analysis of game logs
   - Immediate configuration update when a new port is detected

3. **Improve robustness**:
   - Better error handling in all components
   - Continuous monitoring of configuration changes
