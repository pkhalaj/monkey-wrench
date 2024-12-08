SOURCE_DIR := source

.DEFAULT_GOAL := html
.PHONY: clean html

clean:
	@cd $(SOURCE_DIR) && find . -type f -name 'monkey_*.rst' -delete && rm -fr *build
	@cd $(SOURCE_DIR) && find . -type d -name 'static' ! -path './static' -exec rm -rf {} +

html:
	@cd $(SOURCE_DIR) && python -m sphinx -T -b html -d _build/doctrees -D language=en . build/html
