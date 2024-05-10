#!/bin/bash
cd apps
celery -A procollab_skills worker --beat --loglevel=debug
