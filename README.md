# Development

The majority of code is in [cnxtransforms/xsl/cnxml-to-html5.xsl](cnxtransforms/xsl/cnxml-to-html5.xsl)

# Testing

Rebuild the snapshots:

```sh
py.test --cov=cnxtransforms --ignore=src --snapshot-update 
```