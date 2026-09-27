NAME  := phil_genera_cv
BUILD := build
DIST  := dist

.PHONY: all clean check fmt

all: $(DIST)/$(NAME).pdf $(DIST)/index.html $(DIST)/$(NAME).md check

$(BUILD)/$(NAME).tex $(BUILD)/index.html $(BUILD)/$(NAME).md &: cv.yaml build.py boston_map.py templates/cv.tex templates/site.html $(wildcard templates/fonts/*.woff2)
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

clean:
	rm -rf $(BUILD)
