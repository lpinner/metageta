# Checkout the build scripts #
> ## Command-line access ##
> If you plan to make changes, use this command to check out the code as yourself using HTTPS:
```
    # Project members authenticate over HTTPS to allow committing changes.
    svn checkout https://metageta.googlecode.com/svn/build/ build --username <your googlecode username>
```
> When prompted, enter your generated [/hosting/settings googlecode.com] password.

> Use this command to anonymously check out the latest project source code:
```
    # Non-members may check out a read-only working copy anonymously over HTTP.
    svn checkout http://metageta.googlecode.com/svn/build/ build-read-only
```

> ## GUI and IDE access ##
> This project's Subversion repository may be accessed using many different client programs and plug-ins. See your client's documentation for more information.  I use [TortoiseSVN](http://tortoisesvn.tigris.org) on Windows or [RabbitVCS](http://rabbitvcs.org) on Linux.