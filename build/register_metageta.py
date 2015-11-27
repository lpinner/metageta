import os, shutil, site, sys, tempfile
import _winreg as winreg


crawl_script = 'metagetacrawler.exe'
trans_script = 'metagetatransform.exe'
config_script = 'metagetaconfig.exe'
crawl_lnk = 'MetaGETA Crawler.lnk'
trans_lnk = 'MetaGETA Transform.lnk'
config_lnk = 'MetaGETA Config.lnk'


def add_to_start_menu(start_menu, script_dir):
    start_menu = os.path.join(get_special_folder_path(start_menu), 'MetaGETA')
    icon = os.path.join(script_dir, 'metageta.ico')
    if not os.path.exists(icon):
        icon = ''

    if os.path.exists(start_menu):
        if os.path.isdir(start_menu): shutil.rmtree(start_menu)
        else: os.unlink(start_menu)
    os.makedirs(start_menu)
    directory_created(start_menu)

    tmpdir = tempfile.mkdtemp()

    script = os.path.join(script_dir, crawl_script)
    tmplnk = os.path.join(tmpdir, crawl_lnk)
    startlnk = os.path.join(start_menu, crawl_lnk)
    create_shortcut(script, 'MetaGETA Crawler', tmplnk, '', '', icon)
    shutil.move(tmplnk, startlnk)
    file_created(startlnk)

    script = os.path.join(script_dir, trans_script)
    tmplnk = os.path.join(tmpdir, trans_lnk)
    startlnk = os.path.join(start_menu, trans_lnk)
    create_shortcut(script, 'MetaGETA Transform', tmplnk, '', '', icon)
    shutil.move(tmplnk, startlnk)
    file_created(startlnk)

    script = os.path.join(script_dir, config_script)
    tmplnk = os.path.join(tmpdir, config_lnk)
    startlnk = os.path.join(start_menu, config_lnk)
    create_shortcut(script, 'MetaGETA Config', tmplnk, '', '', icon)
    shutil.move(tmplnk, startlnk)
    file_created(startlnk)

    shutil.rmtree(tmpdir, ignore_errors=True)


def create_keys(reg_root, script_dir):

    script = os.path.join(script_dir, crawl_script)

    key = winreg.CreateKey(reg_root, r'Software\Classes\Directory\shell\metageta')
    winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'MetaGETA Crawler...')
    key.Close()
    key = winreg.CreateKey(reg_root, r'Software\Classes\Directory\shell\metageta\Command')
    winreg.SetValueEx(key, '', 0, winreg.REG_EXPAND_SZ, '"%s" -d "%%1"'%script)
    key.Close()
    key = winreg.CreateKey(reg_root, r'Software\Classes\Directory\Background\shell\metageta')
    winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'MetaGETA Crawler...')
    key.Close()
    key = winreg.CreateKey(reg_root, r'Software\Classes\Directory\Background\shell\metageta\Command')
    winreg.SetValueEx(key, '', 0, winreg.REG_EXPAND_SZ, '"%s" -d "%%V"'%script)
    key.Close()


def delete_keys(reg_root):
    winreg.DeleteKey(reg_root, r'Software\Classes\Directory\shell\metageta\Command')
    winreg.DeleteKey(reg_root, r'Software\Classes\Directory\shell\metageta')
    winreg.DeleteKey(reg_root, r'Software\Classes\Directory\Background\shell\metageta\Command')
    winreg.DeleteKey(reg_root, r'Software\Classes\Directory\Background\shell\metageta')


if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.exit(0)

    if sys.argv[1] == '-install':
        for start_menu, reg_root, install_dir in (
                ('CSIDL_COMMON_STARTMENU', winreg.HKEY_LOCAL_MACHINE, sys.exec_prefix),
                ('CSIDL_STARTMENU', winreg.HKEY_CURRENT_USER, site.USER_BASE)):

            script_dir = os.path.join(install_dir, 'Scripts')

            try:
                try:delete_keys(reg_root)
                except:pass
                create_keys(reg_root, script_dir)
                add_to_start_menu(start_menu, script_dir)
                break
            except:
                continue

    elif sys.argv[1] == '-remove':
        for reg_root in winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER:
            try:
                delete_keys(reg_root)
                break
            except:
                continue

