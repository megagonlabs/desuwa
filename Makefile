
all: lint lint_markdown test

GREP_EXCLUDE_DIR:=grep -v -e '\.eggs' -e '\.git' -e 'pyc$$' -e '\.idea' -e '\./venv' -e 'python_env'  -e 'egg-info' -e htmlcov

POETRY_NO_ROOT:= --no-root
TARGET_DIR:=desuwa

dev_setup:
	poetry install $(POETRY_NO_ROOT) $(POETRY_OPTION)

setup: setup_python setup_npm

setup_python:
	poetry install $(POETRY_OPTION)

setup_npm:
	npm install

flake8:
	find $(TARGET_DIR) ./tests *.py | grep -v '\.venv' | grep '\.py$$' | xargs flake8
black:
	find $(TARGET_DIR) ./tests *.py | grep -v '\.venv' | grep '\.py$$' | xargs black --diff | diff /dev/null -
isort:
	find $(TARGET_DIR) ./tests *.py | grep -v '\.venv' | grep '\.py$$' | xargs isort --diff | diff /dev/null -

jsonlint:
	find .*json $(TARGET_DIR) ./tests -type f |  grep '\.jsonl$$' | sort |xargs cat | python3 -c 'import sys,json; [json.loads(line) for line in sys.stdin]'
	find .*json $(TARGET_DIR) ./tests -type f |  grep '\.json$$' | sort |xargs -n 1 -t python3 -m json.tool > /dev/null
	find .*json $(TARGET_DIR) ./tests -type f |  grep '\.json$$' | sort |xargs -n 1 -t jsonlint
	python3 -c "import sys,json;print(json.dumps(json.loads(sys.stdin.read()),indent=4,ensure_ascii=False,sort_keys=True))" < .markdownlint.json  | diff -q - .markdownlint.json

pyright:
	npx pyright

yamllint:
	yamllint --no-warnings ./.circleci/config.yml

lint: flake8 black pyright isort yamllint

_run_isort:
	isort -rc .

_test:
	coverage run -m unittest discover

_coverage:
	python3 -m unittest discover tests

test: _test _coverage

test-coverage: test
	coverage report && coverage html

CC_REPORTER_VERSION:=0.6.3
setup-cc:
	mkdir -p ~/.local/bin-cc
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-$(CC_REPORTER_VERSION)-linux-amd64 > ~/.local/bin-cc/cc-test-reporter
	chmod +x ~/.local/bin-cc/cc-test-reporter
	~/.local/bin-cc/cc-test-reporter before-build

test-cc: test
	coverage xml && \
	    ~/.local/bin-cc/cc-test-reporter after-build\
	    --coverage-input-type coverage.py\
	    --exit-code $$?

lint_markdown:
	find . -type d -o -type f -name '*.md' -print \
                | grep -v node_modules \
                | grep -v '\.venv' \
                | xargs npx markdownlint --config ./.markdownlint.json

.PHONY: all setup \
	flake8 black pyright isort jsonlint yamllint\
	terms_check_path term_check_method term_check_file_content\
	lint \
	_run_isort _test _coverage\
	test test-coverage setup-cc test-cc\
	setup_npm lint_markdown circleci_local

.DELETE_ON_ERROR:

circleci_local:
	circleci local execute
