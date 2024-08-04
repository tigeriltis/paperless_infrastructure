#!/bin/bash
CONSUME_DIR="SETMECORRECTLY"
if [ $# -eq 0 ] ; then echo Give at least one file or folder to consume as argument. ; exit ; fi
## exclude ~*             -> anything that start with a ~
## exclude .git           -> .git repository directories
## include *.<extension>  -> supported and wanted filetypes
## include */             -> parse all directories
## exclude *              -> anything else
rsync -av --no-owner --no-group --exclude=~* --exclude=.git --include=*/ --include=\*.{pdf,jpeg,jpg,png,tif,gif,txt,rtf,odt,ods,odp,doc,docx,ppt,pptx,xls,xlsx,eml} --exclude=\* $@ "${CONSUME_DIR}"
