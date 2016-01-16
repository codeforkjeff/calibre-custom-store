
calibre-custom-store
====================

A configurable OpenSearch store plugin for [calibre](http://calibre-ebook.com/)


Features
--------

* Uses calibre's built-in support for the [OpenSearch API](http://www.opensearch.org/)
* Allows store configuration under Preferences -> Plugins -> Store plugins
* Supports login authentication and custom login handlers


Install
-------

Download the latest .zip file under releases.

Open calibre, and go to Preferences -> Plugins -> Store plugins

Click "Load plugin from file" and select the .zip file

Find and select "Custom Store" in the list of store plugins

Click "Customize plugin" and set the appropriate values. If you change the store name, you'll need to restart calibre.

Click the "Get Books" button. Your new store should appear in the left pane and be searchable.


A Note about Password Storage
-----------------------------

Please note that your password is obfuscated but NOT securely stored in a .json preferences file!


Development
-----------

```
# clone this repository
git clone ...

# install plugin and run calibre in debug mode
calibre-debug -s; calibre-customize -b calibre-custom-store/src/; calibre-debug -g
```

See auth.py if you want to write your own login handler.
