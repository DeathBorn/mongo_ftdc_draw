===========
MongoDB FTDC visualization tool
===========

Typical usageoften looks like this::

    usage: mongo_ftdc_draw [-h] -f FILE -o OUT_FILE [-s SCHEME] [-d DATEMARKS]
                       [-v | -q]

	FTDC drawer

	optional arguments:
	  -h, --help            show this help message and exit
	  -f FILE, --file FILE  decoded diagnostic file, in JSON (default: None)
	  -o OUT_FILE, --output OUT_FILE
	                        plot filename (example.png) (default: None)
	  -s SCHEME, --scheme SCHEME
	                        metric scheme: main|... (default: main)
	  -d DATEMARKS, --datemarks DATEMARKS
	                        datemarks'\{"name":"date"\}' (default: {})
	  -v, --verbose         verbose (default: False)
	  -q, --quiet           quiet (default: False)

