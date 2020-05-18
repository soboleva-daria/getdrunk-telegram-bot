CODE = get_drunk_telegram_bot scripts tests

lint:
	black --target-version py36 --check --skip-string-normalization $(CODE)
	flake8 --jobs 4 --statistics $(CODE)
	pylint --jobs 4 --rcfile=setup.cfg $${TEAMCITY_VERSION:+$(TC_ARGS)} $(CODE)
	mypy $(CODE)

pretty:
	black --target-version py36 --skip-string-normalization $(CODE)
	isort --apply --recursive $(CODE)
	unify --in-place --recursive $(CODE)