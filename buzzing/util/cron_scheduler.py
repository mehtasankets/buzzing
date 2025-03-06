"""Utility for cron-based scheduling."""
import asyncio
import logging
from datetime import datetime
from croniter import croniter

logger = logging.getLogger(__name__)

class CronScheduler:
    """Scheduler that executes tasks based on cron expressions."""

    @staticmethod
    def is_valid_cron(cron_expr: str) -> bool:
        """Check if a cron expression is valid.
        
        Args:
            cron_expr: The cron expression to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            croniter(cron_expr, datetime.now())
            return True
        except Exception as e:
            logger.error(f"Invalid cron expression '{cron_expr}': {e}")
            return False

    @staticmethod
    async def schedule_task(cron_expr: str, task_func, *args, **kwargs):
        """Schedule a task to run according to a cron expression.
        
        Args:
            cron_expr: The cron expression for scheduling
            task_func: The async function to execute
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
        """
        if not CronScheduler.is_valid_cron(cron_expr):
            raise ValueError(f"Invalid cron expression: {cron_expr}")

        cron = croniter(cron_expr, datetime.now())
        while True:
            try:
                # Get next execution time
                next_time = cron.get_next(datetime)
                now = datetime.now()
                
                # Calculate sleep duration
                sleep_seconds = (next_time - now).total_seconds()
                if sleep_seconds > 0:
                    await asyncio.sleep(sleep_seconds)
                
                # Execute the task
                try:
                    await task_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing scheduled task: {e}")
            except Exception as e:
                logger.error(f"Error in cron scheduler: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying on error
