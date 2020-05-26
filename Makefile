CODE = get_drunk_telegram_bot scripts tests

lint:
	flake8 --jobs 4 --statistics $(CODE)
	mypy $(CODE)

pretty:
	black --target-version py36 --skip-string-normalization $(CODE)
	isort --apply --recursive $(CODE)
	unify --in-place --recursive $(CODE)