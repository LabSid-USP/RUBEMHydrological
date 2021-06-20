@ECHO OFF

::QGIS Installation Path
set OSGEO4W_ROOT=C:\\PROGRA~1\\QGIS\\

set PATH=%OSGEO4W_ROOT%\bin;%PATH%
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\qgis\bin

@echo off
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
call "%OSGEO4W_ROOT%\bin\py3_env.bat"
@echo off
path %OSGEO4W_ROOT%\apps\qgis\bin;%OSGEO4W_ROOT%\apps\grass\grass78\lib;%OSGEO4W_ROOT%\apps\grass\grass78\bin;%PATH%

cd /d %~dp0

@ECHO ON

::Ui Compilation
call pyuic5 --import-from . ..\rubem_hydrological_dialog_base.ui -o ..\rubem_hydrological_dialog_base_ui.py          

::Resources
call pyrcc5 ..\resources.qrc -o ..\resources_rc.py

@ECHO OFF
GOTO END

:ERROR
   echo "Failed!"
   set ERRORLEVEL=%ERRORLEVEL%
   pause

:END
@ECHO ON