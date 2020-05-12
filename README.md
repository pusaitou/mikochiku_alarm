
## TEST : One config.spec to different platform binary.

### Concept **2** : Stores the raw resource files to the distribution directory instead of storing them to the .exe file.

+ All raw resource files are stored in the 'res' directory.

+ Deplicate `resource_path()` function. The run codes are same between while developing and executing.

### Pros : 
+ Code maintenance becomes easy: 
+ + We do not have to maintain config.spec.
+ + No need to use resource_path() function in main script.

### Cons :
+ The extracted directory of user is not clean (.exe file and resource directory).
