@echo off
RMDIR /s /q "C:\Users\hje\Documents\Bots\botsdev\build"
DEL /Q "C:\Users\hje\Documents\Bots\botsdev\MANIFEST"
RMDIR /s /q "C:\Users\hje\Documents\Bots\botsdev\bots.egg-info"


MOVE /Y "C:\Users\hje\Documents\Bots\botsdev\bots\config\bots.ini"         "C:\Users\hje\Documents\Bots\abots"
MOVE /Y "C:\Users\hje\Documents\Bots\botsdev\bots\config\settings.py"      "C:\Users\hje\Documents\Bots\abots"
MOVE /Y "C:\Users\hje\Documents\Bots\botsdev\bots\botssys\sqlitedb\botsdb" "C:\Users\hje\Documents\Bots\abots"


ECHO build exe
DEL /Q "C:\Users\hje\Documents\Bots\botsdev\setup.py"
COPY /Y "C:\Users\hje\Documents\Bots\botsdev\setup_win.py" "C:\Users\hje\Documents\Bots\botsdev\setup.py"
REM ~ c:\python26\python setup.py --quiet bdist_wininst  --target-version=2.6 --install-script=postinstallation.py  --no-target-compile  --no-target-optimize  --user-access-control=auto --bitmap=botslogo.bmp --title="Bots open source edi translator"
REM c:\python27\python setup.py --quiet bdist_wininst   --install-script=postinstallation.py  --no-target-compile  --no-target-optimize  --user-access-control=force --bitmap=botslogo.bmp --title="Bots open source edi translator"
c:\python27-64\python setup.py --quiet bdist_wininst   --install-script=postinstallation.py  --no-target-compile  --no-target-optimize  --user-access-control=force --bitmap=botslogo.bmp --title="Bots open source edi translator"


REM COPY /Y "C:\Users\hje\Documents\Bots\botsdev\bots\install\settings.py"  "C:\Users\hje\Documents\Bots\botsdev\bots\config"
REM COPY /Y "C:\Users\hje\Documents\Bots\botsdev\bots\install\bots.ini"     "C:\Users\hje\Documents\Bots\botsdev\bots\config"
REM COPY /Y "C:\Users\hje\Documents\Bots\botsdev\bots\install\botsdb"       "C:\Users\hje\Documents\Bots\botsdev\bots\botssys\sqlitedb"


MOVE /Y "C:\Users\hje\Documents\Bots\abots\botsdb"       "C:\Users\hje\Documents\Bots\botsdev\bots\botssys\sqlitedb" 
MOVE /Y "C:\Users\hje\Documents\Bots\abots\bots.ini"     "C:\Users\hje\Documents\Bots\botsdev\bots\config"
MOVE /Y "C:\Users\hje\Documents\Bots\abots\settings.py"  "C:\Users\hje\Documents\Bots\botsdev\bots\config" 


RMDIR /s /q "C:\Users\hje\Documents\Bots\botsdev\build"
DEL /Q "C:\Users\hje\Documents\Bots\botsdev\MANIFEST"
ECHO BUILD FINISHED
