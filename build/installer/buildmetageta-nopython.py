# -*- coding: UTF-8 -*-
'''
    Build the MetaGETA download packages, including the GDAL library, no python, no installer

    Usage: buildmetageta-nopython.py [-v version]
    Where: version = tagged release number (e.g. 1.2), "curr" - latest release, "trunk" - unstable dev.

    NOTE:
        * Versions <= 1.2 only work with OSGeo4W/Python25 binaries.
          You need to override setenv.py defaults with environment variables before running the build.
        * This script relies on the following svn properties being set (and kept up to date)
            version (N.N.N.N format)
            displayversion (free text, e.g 1.4 RC1)

'''
import os,sys,shutil,glob,tempfile,zipfile as zip, fnmatch, optparse,time

sys.path.append('..')
sys.path.append(os.path.dirname(os.path.dirname(sys.argv[0])))
from setenv import BIN_DIR,DOWNLOAD_DIR,TOPDIR,PY_DIR
from utilities import rglob,which,runcmd

#Allow overwriting of the environment variables
def main(vers=None):
    try:
        if vers:pause=False
        else:pause=True

        svn=which('svn')

        if not svn:
            print 'Install an SVN command line client (e.g. http://www.sliksvn.com) or ensure that it is on your PATH'
            if pause:raw_input('Press enter to exit.')
            sys.exit(1)

        if not vers:
            try:vers = raw_input('Enter the version to build, options are: \n1.N (eg. 1.1 release) \ncurr (latest release) \nbranches/<branch> \ntrunk (unstable development) \nVersion:  ')
            except:sys.exit(0)#vers = 'trunk'

        repo=''
        if vers in ['curr','']:
            cmd='svn ls http://metageta.googlecode.com/svn/tags'
            exit_code,stdout,stderr=runcmd(cmd)
            if exit_code != 0:
                if stderr:    print stderr
                elif stdout:  print stdout
                else :        print 'SVN command failed'
                if pause:raw_input('Press enter to exit.')
                sys.exit(exit_code)
            else:
                vers=stdout.strip().split()[-1][:-1]
                'tags/%s'%vers
                print 'Latest release is %s'%vers

        elif vers[-4:]=='curr':  #i.e. branches/dsewpac/curr
            cmd='svn ls http://metageta.googlecode.com/svn/%s/tags'%vers[:-5]
            exit_code,stdout,stderr=runcmd(cmd)
            if exit_code != 0:
                if stderr:    print stderr
                elif stdout:  print stdout
                else :        print 'SVN command failed'
                if pause:raw_input('Press enter to exit.')
                sys.exit(exit_code)
            else:
                repo='%s/tags/'%vers[:-5]
                vers=stdout.strip().split()[-1][:-1]
                repo+=vers
                print 'Latest release is %s'%vers

        cd = os.path.abspath(os.path.dirname(sys.argv[0]))

        os.chdir(cd)
        tmp=tempfile.mkdtemp(dir=cd)
        if not os.path.exists(DOWNLOAD_DIR):os.mkdir(DOWNLOAD_DIR)

        ##########################################################
        ##Get revision
        if not repo:
            if 'branches' in vers or 'trunk' in vers :repo=vers
            else:repo='tags/'+vers

        cmd='svn info http://metageta.googlecode.com/svn/%s'%repo
        exit_code,stdout,stderr=runcmd(cmd)
        if exit_code != 0:
            print stderr
            if pause:raw_input('Press enter to exit.')
            cleanup(tmp)
            sys.exit(exit_code)

        for line in stdout.split('\n'):
            line=line.split(':')
            if line[0].strip()=='Last Changed Rev':
                rev=line[1].strip()
                break

        cmd='svn propget version http://metageta.googlecode.com/svn/%s'%repo
        exit_code,stdout,stderr=runcmd(cmd)
        if exit_code != 0:
            print stderr
            if pause:raw_input('Press enter to exit.')
            cleanup(tmp)
            sys.exit(exit_code)
        version=stdout.strip().replace('$Revision$',rev)

        cmd='svn propget displayversion http://metageta.googlecode.com/svn/%s'%repo
        exit_code,stdout,stderr=runcmd(cmd)
        if exit_code != 0:
            print stderr
            if pause:raw_input('Press enter to exit.')
            cleanup(tmp)
            sys.exit(exit_code)
        displayversion=stdout.strip().replace('$Revision$',rev)

        if not version: #Just in case the svn props are not set
            if 'trunk' in vers :
                version='0.0.0.%s'%(vers.replace('/','-'),rev)
            else:
                if vers.count('.')==0:
                    vers=vers+'.0.0.'+rev
                elif vers.count('.')==1:
                    vers=vers+'.0.'+rev
                elif vers.count('.')==2:
                    vers=vers+'.'+rev
                outfile=vers
        if not displayversion:
            if 'trunk' in vers :
                displayversion='%s-%s'%(vers.replace('/','-'),rev)
            else:
                displayversion=vers
        outfile=displayversion.replace(' ','-').lower()
        ##########################################################
        print 'Cleaning up compiled objects'
        for pyco in rglob(BIN_DIR,'*.py[c|o]'):
            os.remove(pyco)

        ##########################################################
        print 'Exporting from SVN repo'
        #cmd='svn export -q --force http://metageta.googlecode.com/svn/%s %s/metageta'%(repo,tmp)

        #DSEWPaC web filter blocks svn:external .bat files with svn export, use checkout
        #instead, then export from the local copy and remove it after
        cmd='svn checkout http://metageta.googlecode.com/svn/%s %s/metageta-svn'%(repo,tmp)
        exit_code,stdout,stderr=runcmd(cmd)
        if exit_code != 0:
            if stderr:    print stderr
            elif stdout:  print stdout
            else :        print 'SVN export failed'
            cleanup(tmp)
            if pause:raw_input('Press enter to exit.')
            sys.exit(exit_code)

        cmd='svn export %s/metageta-svn %s/metageta'%(tmp,tmp)
        exit_code,stdout,stderr=runcmd(cmd)
        if exit_code != 0:
            if stderr:    print stderr
            elif stdout:  print stdout
            else :        print 'SVN export failed'
            cleanup(tmp)
            if pause:raw_input('Press enter to exit.')
            sys.exit(exit_code)

        #Clean up the .svn dirs
        shutil.rmtree('%s/metageta-svn'%tmp)

        ##########################################################
        f=open('%s\\version.txt'%tmp,'w').write('Version: %s'%displayversion)
        for f in glob.glob('include\\Run*.lnk'):shutil.copy(f,tmp)

        ##########################################################
        def ignore_patterns(*patterns):
            """Function that can be used as copytree() ignore parameter.

            Patterns is a sequence of glob-style patterns
            that are used to exclude paths

            Code modified from PSF licensed shutil.ignore_patterns"""
            patterns=[p.replace('/',os.sep).replace('\\',os.sep) for p in patterns]
            def _ignore_patterns(path, names):
                ignored_names = []
                filepaths=[os.path.join(path,n) for n in names]
                for pattern in patterns:
                    ignored_paths=fnmatch.filter(filepaths,pattern)
                    ignored_names.extend([os.path.basename(n) for n in ignored_paths])
                return set(ignored_names)
            return _ignore_patterns
        ignore=ignore_patterns('*/gdal/bin/*.py','*.pyc','*.exe','*.bat','*.cmd','*/plugins.disabled')
        shutil.copytree(os.path.join(BIN_DIR,'gdal'), os.path.join(tmp,'gdal'),ignore=ignore)
        ignore=ignore_patterns('*.exe','*.bat','*.cmd','*/epydoc')
        shutil.copytree(os.path.join(PY_DIR,'Lib','site-packages'), os.path.join(tmp,'python','Lib','site-packages'),ignore=ignore)

        ##########################################################
        print 'Zipping files'
        fout=DOWNLOAD_DIR+'\\metageta-%s.zip'%outfile
        zout=zip.ZipFile(fout,'w',zip.ZIP_DEFLATED)

        #Code only
        for f in rglob(tmp):
            if not os.path.isdir(f):
                zout.write(f,f.replace(tmp,'metageta'))
        zout.close()

    except Exception,err:
        print err

    cleanup(tmp)
    if pause:raw_input('Press enter to exit.')

def cleanup(*args):
    for arg in args:
        if os.path.isdir(arg):
            try:shutil.rmtree(arg)
            except Exception,err:
                print err
        elif os.path.isfile(arg):
            try:os.remove(arg)
            except Exception,err:
                print err
        else:pass

if __name__=='__main__':
    parser = optparse.OptionParser(description='Build the MetaGETA installer')
    vers_help='The version to build, options are: \n1.N (eg. 1.1 release) \ncurr (latest release) \nbranches/<branch> \ntrunk (unstable development)'
    opt=parser.add_option('-v', dest="vers", metavar="vers",help=vers_help)
    optvals,argvals = parser.parse_args()
    main(optvals.vers)