#!/bin/bash

function sendmail {
	curl -s --user 'key-0cb37ccb0c2de16fc921df70228346bc' \
		https://api.mailgun.net/v3/efficacite21.com/messages \
	   -F from='Bot Futur<noreply@blousebrothers.fr>' \
       	   -F to='guillaume@blousebrothers.fr' \
       	   -F cc='julien@blousebrothers.fr' \
       	   -F subject="$1" \
       	   -F text="$2"
}

git fetch origin master
log=`git log --pretty=oneline --abbrev-commit ..origin/master`
git merge
sendmail "http://futur.blousebrothers.fr:8000 updated" "$log"

