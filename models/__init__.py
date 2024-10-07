#!/usr/bin/python3
"""Module for initializing the storage instance"""

from .storage import Storage

# Initialize the storage instance for use throughout the project
storage = Storage()
storage.reload()
