#!/bin/bash
CONSUME_DIR="SETMECORRECTLY"
if [ $# -eq 0 ] ; then echo Give at least one file or folder to consume as argument. ; exit ; fi
## exclude ~*             -> anything that start with a ~
## exclude .git           -> .git repository directories
## include *.<extension>  -> supported and wanted filetypes
## include */             -> parse all directories
## exclude *              -> anything else
rsync -av --no-owner --no-group --exclude=~* --exclude=.git --include=*/ --include=\*.{pdf,jpeg,jpg,png,tif,gif,txt,rtf,odt,ods,odp,doc,docx,ppt,pptx,xls,xlsx,eml} --exclude=\* $@ "${CONSUME_DIR}"


## When consumption of PDF fails with: mime-type not supported: application/octet-stream or data/octet-stream
## you can identify the pdfs in the filesystem with:
#find -iname *.pdf -exec file --mime-type {} \; | grep -v "application/pdf"
## a way to convert the pdfs from application/octet-stream is to open and save it in any pdf viewer
## it for example works with pdftk as follows:
#for i in *.pdf ; do pdftk $i output ${CONSUME_DIR}/$i ; done

