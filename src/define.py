import os

WINDOW_WIDTH=350
WINDOW_HEIGHT=595
GENIUS_API_TOKEN="_Pe-HxIj6CNGImdRIcenX_4D51FvShKKQlQDP52NSMfcsOKaDd3r1CguBtbuT4ht"
if os.name=="posix":
    DB_PATH=os.path.expanduser('~/.config/aoede.db')
if os.name=="nt":
    DB_PATH=os.path.expanduser('~\\Documents\\aoede.db')