## Tools
## Backup
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203

#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --reindex
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update

#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w rsshistory
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w catalog
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w private
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w programming
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w threed
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w various
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w vr
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa --sequence-update -w places

#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w catalog
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w places
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w private
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w programming
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w rsshistory
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w threed
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w various
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f custom --host 192.168.0.203 -w vr

poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w catalog
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w catalog
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w places
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w private
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w programming
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w rsshistory
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w threed
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w various
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -b -f sqlite --host 192.168.0.203 -w vr

## Restore
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w rsshistory
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w catalog
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w private
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w programming
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w threed
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w various
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w vr
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f custom -w places

#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f sqlite --append -w places
#poetry run python backup.py -U pi -d pi -p O0mpaLO0mpa -r -f sqlite -w places

## Test
# psql -U pi -d pi -p O0mpaLO0mpa -h 127.0.0.1
