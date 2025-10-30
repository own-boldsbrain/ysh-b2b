#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper para executar pipeline com DATABASE_URL correto"""
import os
import subprocess
import sys

# Set correct DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/ysh_solar"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# Run the actual pipeline
sys.exit(subprocess.call([sys.executable, "scripts/data_extraction_pipeline.py"]))
