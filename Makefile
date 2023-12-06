lint:
	. .venv/bin/activate && \
	pylint plugin.video.external.library/libs \
		plugin.video.external.library/main.py\
		plugin.video.external.library/commands.py \
		plugin.video.external.library/service.py

PHONY: lint

check:
	kodi-addon-checker --branch nexus plugin.video.external.library

PHONY: check
