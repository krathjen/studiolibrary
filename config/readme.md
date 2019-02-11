
## Config

There are two ways to create a custom config.

1. You can create a config.json file in this directory.
The config.json file will override any keys in the [default.json](../src/studiolibrary/config/default.json) file
and will be ignored by git.

2. The other way is to create an environment variable with the name
STUDIO_LIBRARY_CONFIG_PATH. The value of this variable should be the
full path to your config.json file.

The config uses the json file type with basic support for comments using "//".

##### Example:

```javascript
// config.json
{
  // The maximum walking depth from the root directory
  "recursiveSearchDepth": 4
}
```

