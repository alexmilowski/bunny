# bunny
A simple task operation library to "hop" from state to state that handles
various parameterization and packaging. Useful for bundling python programs
for containerization and all configured by JSON.

## An Example

A sample bundle file (`bundle.json`) that puts to `start_job.py` and `delete_output.py`:

```
{
   "@type" : "Bundle",
   "@context" : {
      "date" : { "@type" : "xsd:date" }
   },
   "start" : {
      "script" : "start_job",
      "arguments" : [
         { "@type": "ArgumentSet", "name" : "knox"},
         "{base_dir}/start_job.zip",
         "/Data/{date_Y:04}/{date_m:02}/{date_d:02}/xfers_{date_y:02}{date_m:02}{date_d:02}.csv",
         "{output_dir}/{date_Y:04}-{date_m:02}-{date_d:02}.csv"
      ]
   },
   "delete" : {
      "script" : "delete_output",
      "arguments" : [
         { "@type": "ArgumentSet", "name" : "knox"},
         "{output_dir}/{date_Y:04}-{date_m:02}-{date_d:02}.csv"
      ]
   }
}
```

A sample configuration file (`bunny.json`):

```
{
   "arguments" : {
      "knox" : [
         "--base",
         "https://knox.example.com/",
         "--no-verify",
         "--gateway",
         "bigdata",
         "--auth",
         "user:password"
      ]
   },
   "values" : {
      "output_dir" : "/Data/Output/"
   }
}
```

A sample invocation:

```
python -m bunny -c bunny.json bundle.json start -p date 2018-10-28
```

which invokes `start_job.py` with the arguments from the fixed argument
set `knox`, the fixed value `output_dir`, and the parameter `date`. Since
the `date` parameter is typed as `xsd:date`, the value is parsed and split
into fields (Y,y,m,d) and the preceding and following dates are also calculated.
All these variants are directly usable in the formatted strings.

Each argument can be templated against the computed parameters using format
strings.

The python module is loaded and run with the computed arguments list.

# Configuration

...more to follow...
