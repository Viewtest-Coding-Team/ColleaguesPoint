web: gunicorn linkedin_app:linkedin_app -t gthread -w 4 -b 0.0.0.0:$PORT --max-requests=1000 --timeout 90 --worker-tmp-dir /dev/shm --preload
