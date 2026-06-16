#!/usr/bin/env bash
# Regenerate all Word/PDF deliverables for the ScienceDirect submission.
set -e
cd "$(dirname "$0")"

echo ">> Manuscript: main.tex -> main.docx"
python3 preprocess_word.py                       # main.tex -> main_word.tex (pandoc-friendly tables)
pandoc main_word.tex --from=latex --to=docx \
  --resource-path=.:figs \
  --bibliography=references.bib --citeproc \
  --metadata reference-section-title="References" \
  -o main.docx
python3 fix_docx.py                              # reinsert affiliation/emails, fix keywords

echo ">> Statements: *.tex -> *.docx + *.pdf"
for f in cover-letter declaration-of-interest credit-author-statement; do
  pandoc "$f.tex" --from=latex --to=docx -o "$f.docx"
  pdflatex -interaction=nonstopmode -halt-on-error "$f.tex" >/dev/null
done
rm -f cover-letter.{aux,log,out} declaration-of-interest.{aux,log,out} credit-author-statement.{aux,log,out}

echo ">> Done. Deliverables:"
ls -1 main.docx cover-letter.docx declaration-of-interest.docx credit-author-statement.docx
