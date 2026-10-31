from enum import Enum


class Status(str, Enum):
    queued = "queued"
    running = "running"
    awaiting_feedback = "awaiting_feedback"
    completed = "completed"
    failed = "failed"
