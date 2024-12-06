SOURCE_DIR := source

.DEFAULT_GOAL := html
.PHONY: clean html

clean:
	@cd $(SOURCE_DIR) && find . -type f ! -name 'index.rst' ! -name 'conf.py' -delete
	@cd $(SOURCE_DIR) && find . -type d -delete

html:
	@cd $(SOURCE_DIR) && python -m sphinx -T -b html -d _build/doctrees -D language=en . build/html
