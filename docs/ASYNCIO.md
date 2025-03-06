# Asyncio Implementation in Buzzing

This document explains how asynchronous programming with `asyncio` is implemented throughout the Buzzing application.

## Overview

Buzzing uses Python's `asyncio` library to manage multiple Telegram bots concurrently. The implementation follows a hierarchical structure:

```
driver.py (Main Event Loop)
└── BotsInteractor (Task Manager)
    └── BotInteractor (Individual Bot Tasks)
```

## Component Details

### 1. Main Event Loop (`driver.py`)

The main event loop is created and managed by `asyncio.run(main())`. It handles:

- Application lifecycle management
- Signal handling for graceful shutdown
- Database connection management
- Error propagation and logging

Key features:
```python
# Create and manage main event loop
asyncio.run(main())

# Signal handling
loop.add_signal_handler(sig, signal_handler)

# Task management
await asyncio.gather(*bots_interactor.tasks)
```

### 2. Bots Manager (`BotsInteractor`)

The `BotsInteractor` class manages multiple bot tasks. It:

- Creates and tracks individual bot tasks
- Handles task initialization and cleanup
- Manages graceful shutdown sequence

Key features:
```python
# Task creation and tracking
task = loop.create_task(bot_interactor.initiate(), name=f"bot_{config.name}")
self.tasks.append(task)

# Task initialization with timeout
done, pending = await asyncio.wait(
    [task],
    timeout=self.task_timeout,
    return_when=asyncio.FIRST_EXCEPTION
)
```

### 3. Individual Bot (`BotInteractor`)

Each `BotInteractor` manages a single Telegram bot. It:

- Handles bot lifecycle (start, stop, polling)
- Manages command handlers and conversations
- Implements graceful shutdown

Key features:
```python
# Bot lifecycle management using context manager
async with self.application:
    await self.application.start()
    # ... bot operations ...
    await self.application.stop()

# Clean shutdown using asyncio.Event
stop_event = asyncio.Event()
await stop_event.wait()
```

## Shutdown Sequence

1. **Signal Handler**:
   - Catches SIGTERM/SIGINT
   - Triggers `stop_bots()`

2. **BotsInteractor Shutdown**:
   - Stops each bot's polling
   - Cancels all tasks
   - Waits for task cleanup

3. **BotInteractor Shutdown**:
   - Sets stop flag
   - Triggers event-based shutdown
   - Cleans up application resources

## Error Handling

1. **Task Level**:
   - Each bot task handles its own exceptions
   - Errors are logged and propagated

2. **Manager Level**:
   - Failed task initialization triggers cleanup
   - All errors are propagated to main loop

3. **Main Loop**:
   - Ensures database cleanup
   - Logs fatal errors
   - Exits gracefully

## Best Practices Implemented

1. **Resource Management**:
   - Context managers for cleanup
   - Proper task cancellation
   - Database connection handling

2. **Concurrency Control**:
   - Task timeouts for initialization
   - Event-based shutdown
   - Proper task tracking

3. **Error Handling**:
   - Comprehensive try-except blocks
   - Error propagation
   - Detailed logging

## Common Operations

### Starting a New Bot
```python
# 1. Create bot instance
bot_interactor = BotInteractor(config, subscriptions, dao)

# 2. Create and track task
task = loop.create_task(bot_interactor.initiate())

# 3. Wait for initialization
done, pending = await asyncio.wait([task], timeout=timeout)
```

### Graceful Shutdown
```python
# 1. Set stop flag
bot_interactor.stop_bot = True

# 2. Wait for stop event
await stop_event.wait()

# 3. Clean up resources
await application.stop()
```

## Debugging Tips

1. **Task Status**:
   - Check `task.done()` for completion
   - Use `task.get_name()` for identification
   - Inspect `task.exception()` for errors

2. **Event Loop**:
   - Use `asyncio.get_running_loop()` to access loop
   - Monitor loop with `loop.get_debug()`

3. **Logging**:
   - All key operations are logged
   - Check `buzzing.log` for detailed history
