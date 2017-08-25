notebook:
	docker-compose run --rm --user `id -u` -e HOME=/app -p 8889:8888 django python manage.py shell_plus --notebook |sed s/8888/8889/
