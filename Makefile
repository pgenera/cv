NAME  := phil_genera_cv
BUILD := build
DIST  := dist

# Reproducible PDF: the date stamp only changes when the content does. The
# pre-commit hook builds with the current time when cv.yaml changes; other
# builds reuse the date in dist/'s PDF while its cv.yaml fingerprint still
# matches, and otherwise fall back to the last commit touching the sources.
ifndef SOURCE_DATE_EPOCH
SOURCE_DATE_EPOCH := $(shell f=$(DIST)/$(NAME).pdf; \
  if [ -f $$f ] && pdfinfo $$f 2>/dev/null | grep -q "sha256:$$(sha256sum cv.yaml | cut -c1-12)"; \
  then date -d "$$(pdfinfo -isodates $$f | awk '/^CreationDate:/ {print $$2}')" +%s; \
  else git log -1 --format=%ct -- cv.yaml templates/cv.tex build.py 2>/dev/null; fi)
endif
export SOURCE_DATE_EPOCH
export FORCE_SOURCE_DATE := 1

.PHONY: all clean check deps fmt hooks svn publish publish-push identify

all: $(DIST)/$(NAME).pdf $(DIST)/index.html $(DIST)/$(NAME).md $(DIST)/og-image.png check

$(BUILD)/$(NAME).tex $(BUILD)/index.html $(BUILD)/$(NAME).md &: cv.yaml build.py boston_map.py osm/map_data.json templates/cv.tex templates/site.html $(wildcard templates/fonts/*.woff2)
	python3 build.py cv.yaml $(BUILD)

# Two passes so hyperref's bookmarks settle.
$(DIST)/$(NAME).pdf: $(BUILD)/$(NAME).tex
	cd $(BUILD) && pdflatex -interaction=nonstopmode -halt-on-error $(NAME).tex >/dev/null \
	  && pdflatex -interaction=nonstopmode -halt-on-error $(NAME).tex >/dev/null \
	  || { tail -30 $(NAME).log; exit 1; }
	@mkdir -p $(DIST)
	cp $(BUILD)/$(NAME).pdf $@

# Link-preview card (og:image): the hero map with name and headline.
$(DIST)/og-image.png: cv.yaml og_image.py boston_map.py osm/map_data.json templates/site.html $(wildcard templates/fonts/*.woff2)
	@mkdir -p $(DIST)
	python3 og_image.py $< $@

$(DIST)/index.html: $(BUILD)/index.html
	@mkdir -p $(DIST)
	cp $< $@

$(DIST)/$(NAME).md: $(BUILD)/$(NAME).md
	@mkdir -p $(DIST)
	cp $< $@

check: $(DIST)/$(NAME).pdf
	@echo "PDF pages: $$(pdfinfo $(DIST)/$(NAME).pdf | awk '/^Pages:/ {print $$2}')"
	@echo "Overfull hboxes: $$(grep -c 'Overfull \\hbox' $(BUILD)/$(NAME).log || true)"

fmt:
	python3 fmt_yaml.py cv.yaml

# Build dependencies, all from apt.
deps:
	sudo apt install $$(grep -v '^\#' debian-packages.txt)

# Use the repo's hooks (githooks/pre-commit formats cv.yaml and rebuilds dist/).
# Once per clone.
hooks:
	git config core.hooksPath githooks

# Full repo, including private/ and CLAUDE.md, goes to SVN.
svn:
	git svn dcommit

# Filtered history goes to GitHub. `publish` is a dry run; `publish-push` pushes.
publish:
	python3 publish.py

publish-push:
	python3 publish.py --push

# Which commit was this PDF built from?  make identify PDF=path/to/file.pdf
identify:
	python3 pdf_source.py $(or $(PDF),$(DIST)/$(NAME).pdf)

clean:
	rm -rf $(BUILD)
