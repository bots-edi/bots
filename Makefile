GH_PAGES_SOURCES = docs license.rst setup.py
ghpages:
	git checkout gh-pages
	rm -rf _build _sources _static _modules
	git checkout master $(GH_PAGES_SOURCES)
	git reset HEAD
	cd docs;
	make -f Makefile html;
	mv -fv _build/html/* ../;
	cd ..;
	rm -rf $(GH_PAGES_SOURCES) _build
	git add -A
	git commit -m "Generated gh-pages" && git push origin gh-pages ; git checkout master
