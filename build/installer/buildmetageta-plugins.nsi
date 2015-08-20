
    ######################################################################
    #      NSIS Installation Script
    #       
    #       This install script requires the following symbols to be 
    #       defined via the /D commandline switch. It is usually run
    #       by the buildmetageta.py script:
    #       
    #       APP_DIR         Relative path to the MetaGETA code
    #       BIN_DIR         Relative path to the GDAL & Python directory
    #       #VERSION         N.N.N.N format version number # todo? not used currently
    #       #DISPLAY_VERSION Version text string           # todo? not used currently
    #       OUTPATH         output installer filepath
    #       
    #       Example:
    #       makensis /DBIN_DIR=..\bin /DAPP_DIR=tmp /DOUTPATH=..\downloads\metageta-plugins-1.2-setup.exe buildmetageta-plugins.nsi
    #       #makensis /DVERSION=1.2.0.123 /DDISPLAY_VERSION=1.2 RC1 /DOUTPATH=..\downloads\metageta-1.2-setup.exe /DBIN_DIR=..\bin /DAPP_DIR=tmp buildmetageta-plugins.nsi
    #
    ######################################################################
    !define /date YEAR "%Y"

    !define APP_NAME "MetaGETA Plugins"
    !define COMP_NAME "Department of Environment"
    !define WEB_SITE "http://environment.gov.au"
    !define COPYRIGHT "${COMP_NAME} © ${YEAR}"
    !define DESCRIPTION "MetaGETA plugin installer"
    !define MUI_WELCOMEFINISHPAGE_BITMAP "graphics\installer.bmp"
    !define MUI_ICON "graphics\metageta.ico"

    var AllUsers
    var CurrUser
    var Installed

    !define NOTINSTALLED_TITLE "${APP_NAME} can not be installed"

    !define NOTINSTALLED_TEXT "The MetaGETA application is not currently installed. \
                               The ${APP_NAME} can not be installed. \
                               Please install MetaGETA first and then try again."

    !define WELCOME_TITLE "Welcome to the ${APP_NAME} Setup Wizard"

    !define WELCOME_TEXT "This wizard will guide you through the installation of the ${APP_NAME}.$\r$\n$\r$\n\
                          Note: these plugins are distributed separately as they contain proprietary binary libaries \
                          which we are required to license separately according to legal advice."

    !define MULTIUSER_INSTALLMODEPAGE_TEXT_TOP "MetaGETA is currently installed in two locations - for any one using this computer and just for you. \
                                                Please select which of these MetaGETA locations you wish to install the plugins to:"

    !define ECW_DESCRIPTION_TEXT "Uses the Erdas ECW JPEG2000 Codec SDK v5.1"

    !define SID_DESCRIPTION_TEXT "Uses the LizardTech GeoExpress DSDK"

    !define MUI_ABORTWARNING_TEXT "Are you sure you wish to abort the MetaGETA plugins installation?"

    ######################################################################

    SetCompressor LZMA
    Name "${APP_NAME}"
    Caption "${APP_NAME}"
    OutFile "${OUTPATH}"
    BrandingText "${APP_NAME}"
    XPStyle on

    ######################################################################

    !define REG_KEY  "Software\MetaGETA"
    !define REG_VAL  "InstallPath"

    !define MUI_WELCOMEPAGE_TITLE_3LINES
    !define MUI_FINISHPAGE_TITLE_3LINES
    !define MULTIUSER_EXECUTIONLEVEL Highest
    !define MULTIUSER_MUI
    !define MULTIUSER_INSTALLMODE_INSTDIR
    !define MULTIUSER_INSTALLMODE_COMMANDLINE
    !define MULTIUSER_NOUNINSTALL

    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${REG_KEY}"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "${REG_VAL}"

    !define MUI_CUSTOMFUNCTION_ABORT onUserAbort

    !include "MultiUser.nsh"
    !include "MUI2.nsh"

   ######################################################################

    #Check MetaGETA is installed
    Var MUI_HeaderTitle
    Var MUI_HeaderText
    !define MUI_WELCOMEPAGE_TITLE "$MUI_HeaderTitle"
    !define MUI_WELCOMEPAGE_TEXT "$MUI_HeaderText"
    !define MUI_PAGE_CUSTOMFUNCTION_PRE welcome_pre
    !insertmacro MUI_PAGE_WELCOME

    ; Install mode page
    !define MUI_PAGE_CUSTOMFUNCTION_PRE installmode_pre
    !insertmacro MULTIUSER_PAGE_INSTALLMODE

    ; Components page
    !define MUI_PAGE_CUSTOMFUNCTION_PRE .onSelChange
    !insertmacro MUI_PAGE_COMPONENTS

    ; ECW/JPEG2000 License page
    !define MUI_PAGE_CUSTOMFUNCTION_PRE ecwjp2_pre
    !insertmacro MUI_PAGE_LICENSE "licenses\license-ecw.rtf"

    ; MrSID License page
    !define MUI_PAGE_CUSTOMFUNCTION_PRE mrsid_pre
    !insertmacro MUI_PAGE_LICENSE "licenses\license-mrsid.rtf"

    ; Instfiles page
    !insertmacro MUI_PAGE_INSTFILES

    ; Finish page
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !insertmacro MUI_PAGE_FINISH

    !insertmacro MUI_LANGUAGE "English"

    ######################################################################

    # default section
    section /o "ECW/JPEG2000" SEC01

        setOutPath "$INSTDIR\metageta\metageta\formats"
        File  "${APP_DIR}\metageta\metageta\formats\ecw.py"
        File  "${APP_DIR}\metageta\metageta\formats\ecwp.py"
        File  "${APP_DIR}\metageta\metageta\formats\jp2.py"
        setOutPath "$INSTDIR\bin\python27\Lib\site-packages\osgeo"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\NCSEcw.dll"
        setOutPath "$INSTDIR\bin\python27\Lib\site-packages\osgeo\gdalplugins"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\gdalplugins\gdal_ECW_JP2ECW.dll"
        setOutPath "$INSTDIR\bin\python27\Lib\site-packages\osgeo\license"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\license\ECW5License.rtf"

    sectionEnd
    section /o "MrSID" SEC02

        setOutPath "$INSTDIR\bin\python27\Lib\site-packages\osgeo"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\lti_dsdk_9.0.dll"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\lti_lidar_dsdk_1.1.dll"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\tbb.dll"
        setOutPath "$INSTDIR\bin\python27\Lib\site-packages\osgeo\gdalplugins"
        File  "${BIN_DIR}\python27\Lib\site-packages\osgeo\gdalplugins\gdal_MrSID.dll"

    sectionEnd

    ; Section descriptions
    !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
      !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "${ECW_DESCRIPTION_TEXT}"
      !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "${SID_DESCRIPTION_TEXT}"
    !insertmacro MUI_FUNCTION_DESCRIPTION_END

    ######################################################################

    ;Installer Functions
    Function .onInit
      Call CheckInstalled
      !insertmacro MULTIUSER_INIT
    FunctionEnd

    Function CheckInstalled
        ReadRegStr $AllUsers HKLM ${REG_KEY} ${REG_VAL}
        ReadRegStr $CurrUser HKCU ${REG_KEY} ${REG_VAL}
        ${If} "$AllUsers" == ""
        ${AndIf} "$CurrUser" == ""
            StrCpy $Installed "FALSE"
        ${Else}
            StrCpy $Installed "TRUE"
        ${EndIf}
    FunctionEnd

    Function welcome_pre
        GetDlgItem $0 $HWNDPARENT 1 ;Next button
        GetDlgItem $1 $HWNDPARENT 2 ;Cancel button

        ${If} "$Installed" == "TRUE"
            StrCpy $MUI_HeaderTitle "${WELCOME_TITLE}"
            StrCpy $MUI_HeaderText "${WELCOME_TEXT}"
        ${Else}
            StrCpy $MUI_HeaderTitle "${NOTINSTALLED_TITLE}"
            StrCpy $MUI_HeaderText "${NOTINSTALLED_TEXT}"
            ShowWindow  $0 0
            SendMessage $1 ${WM_SETTEXT} 0 "STR:Close"
        ${EndIf}
    FunctionEnd

    Function onUserAbort
        ${If} "$Installed" == "TRUE"
            ${IfNot} ${Cmd} `MessageBox MB_YESNO|MB_DEFBUTTON2 "${MUI_ABORTWARNING_TEXT}" IDYES`
               Abort
            ${EndIf}
        ${EndIf}
    FunctionEnd

    Function .onSelChange
        GetDlgItem $0 $HWNDPARENT 1 ;Next > button
        ${If} ${SectionIsSelected} ${SEC01}
        ${OrIf} ${SectionIsSelected} ${SEC02}
            ; Enable Next button
            EnableWindow $0 1
        ${Else}
            ; Disable Next button
            EnableWindow $0 0
        ${EndIf}
    FunctionEnd

    Function ecwjp2_pre
        ${Unless} ${SectionIsSelected} ${SEC01}
            Abort
        ${EndUnless}
    FunctionEnd

    Function mrsid_pre
        ${Unless} ${SectionIsSelected} ${SEC02}
          Abort
        ${EndUnless}
    FunctionEnd

    Function installmode_pre
        #Installed per machine
        ${If} "$AllUsers" != ""
        ${AndIf} "$CurrUser" == ""
            Call MultiUser.InstallMode.AllUsers
            StrCpy $INSTDIR "$AllUsers"
            Abort

        #Installed per user
        ${ElseIf} "$AllUsers" == ""
        ${AndIf} "$CurrUser" != ""
            Call MultiUser.InstallMode.CurrentUser
            StrCpy $INSTDIR "$CurrUser"
            Abort
      ${EndIf}

     #If installed both per machine & per user,
     #$INSTDIR is found/set by MultiUser.nsh in
     #MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY\MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME

    FunctionEnd


    ######################################################################

