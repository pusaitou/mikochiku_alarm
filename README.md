
## TEST : One config.spec to different platform binary.

### Concept **2** : Stores the raw resource files to the distribution directory instead of storing them to the .exe file.

+ All raw resource files are stored in the 'res' directory.

+ In this repo, I do not use the "resource_path()" function as much as possible. Only static (no need to change) resource file (e.g. icon.ico).

### Pros : 
+ Code maintenance becomes easy: 
+ + We do not have to maintain config.spec.
+ + No need to use resource_path() function in main script.
+ It is faster to start the exe file because there is no need to decompress unnecessary files.
 
### Cons :
+ The extracted directory of user is not clean (.exe file and resource directory).

## MEMO:

### Embedded resource files
In order to handle the embedded resource into the exe file, the following settings are required.

+ Describe the name of resource files in the Analysys.datas[] attribute of the config.spec file.
```python
# config.spec
a = Analysis(['mikochiku_alarm.py'], datas=[] ... )

a.datas += [('icon.ico','icon.ico','DATA')]
```

+ The files described in the config.spec are embedded in the executable file and expanded to the temporary directory (%temp%/___MEIxxxxxx) at runtime.

+ In order for the executable file to correctly access %temp%/___MEIxxxxxx at runtime, you need to redirect the file access using the resource_path() function in the main script.

```python
def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

app.setWindowIcon(QIcon(resource_path(settings.ICON)))
```

+ If you don't use the resouce_path() function, when you run the built exe file, the file will not be found and you will be forced to quit.


### .env File

+ When you use `.env`, you need to put the .env file in the same place as the executable or parent directory of the executable.

If the .env file is not in the same place (or parent directory), the following error will occur internally and the program will be forced to close.

```bash
  File "httpreq\__init__.py", line 19, in <module>
  File "logger.py", line 29, in get_logger
  File "logger.py", line 9, in get_logfile_path
  File "ntpath.py", line 117, in join
  File "genericpath.py", line 152, in _check_arg_types
TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
```

+  <b>env does not have the ability to redirect to a resource file.</b>
+ + Therefore, as a rule, resource files embedded with config.spec should be redirected appropriately using the resource_path() function.
+ + The exception is that: the dll files used by python libraries are implicitly called from "%temp%/___MEIxxxxxx", so there is no need to consider redirection on the main script as long as it is specified in config.spec.
```python
# config.spec
a = Analysis(['mikochiku_alarm.py'], datas=[] ... )

# libmpg123.dll is called by pygame library implicitly.
a.datas += [('libmpg123.dll','libmpg123.dll','DATA')]
```


### The significance of using .env
+ Currently, .env is being used for the abstraction of resource file paths. Even if the location of the resource file changes, there is no need to rewrite the main script.
+ The demerit of .env is that it is difficult to rewrite from the application side.
 
