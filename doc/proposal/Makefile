# Makefile to build and cleanup LaTeX data

PROJECT = proposal

all: ${PROJECT}

${PROJECT}:
	pdflatex ${PROJECT}
#	bibtex ${PROJECT}
#	pdflatex ${PROJECT}
#	pdflatex ${PROJECT}

clean:
	rm -f *.aux *.log *.dvi *.bbl *.blg *.ps *.toc *.lof *.lot *.out
	rm -f ${PROJECT}.pdf

