NAME  := phil_genera_cv
BUILD := build
DIST  := dist

# Reproducible PDF: stamp it with the last commit touching its sources, not the
# build time, so it only changes when its content does.
export SOURCE_DATE_EPOCH := $(shell git log -1 --format=%ct -- cv.yaml templates/cv.tex build.py 2>/dev/null)
export FORCE_SOURCE_DATE := 1

.PHONY: all clean check fmt svn publish publish-push

all: $(DIST)/$(NAME).pdf $(DIST)/index.html $(DIST)/$(NAME).md check

$(BUILD)/$(NAME).tex $(BUILD)/index.html $(BUILD)/$(NAME).md &: cv.yaml build.py boston_map.py osm/map_data.json templates/cv.tex templates/site.html $(wildcard templates/fonts/*.woff2)
	python3 build.py cv.yaml $(BUILD)

# Two passes so hyperref's bookmarks settle.
$(DIST)/$(NAME).pdf: $(BUILD)/$(NAME).tex
	cd $(BUILD) && pdflatex -interaction=nonstopmode -halt-on-error $(NAME).tex >/dev/null \
	  && pdflatex -interaction=nonstopmode -halt-on-error $(NAME).tex >/dev/null \
	  || { tail -30 $(NAME).log; exit 1; }
	@mkdir -p $(DIST)
	cp $(BUILD)/$(NAME).pdf $@

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

# Full repo, including private/ and CLAUDE.md, goes to SVN.
svn:
	git svn dcommit

# Filtered history goes to GitHub. `publish` is a dry run; `publish-push` pushes.
publish:
	python3 publish.py

publish-push:
	python3 publish.py --push

clean:
	rm -rf $(BUILD)
