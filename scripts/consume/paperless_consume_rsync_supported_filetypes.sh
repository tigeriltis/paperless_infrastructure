#!/bin/bash
CONSUME_DIR="SETMECORRECTLY"
if [ $# -eq 0 ] ; then echo Give at least one file or folder to consume as argument. ; exit ; fi
rsync -av --exclude=\.git --include=\*/ --include=\*.{pdf,jpeg,jpg,png,tif,gif,txt,odt,ods,odp,doc,docx,ppt,pptx,xls,xlsx,eml} --exclude \* $@ "${CONSUME_DIR}"
