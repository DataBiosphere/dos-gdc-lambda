# dos-gdc-lambda

Presents NCI GDC data over GA4GH compliant methods.

<img src="https://raw.githubusercontent.com/DataBiosphere/dos-gdc-lambda/master/diagram.png" />

We have created a lambda that creates a lightweight layer that can be used to access data in GDC using GA4GH libraries.

The lambda accepts GA4GH requests and converts them into requests against requisite signpost endpoints. The results are then translated into GA4GH style messages before being returned to the client.

To make it easy for developers to create clients against this API, the Open API description is made available.

## Try it out!

Install chalice: `pip install chalice` and try it out yourself!

```
git clone https://github.com/DataBiosphere/dos-gdc-lambda.git
cd dos-gdc-lambda
chalice deploy
```


This will return you a URL you can make GA4GH DOS requests against!

For more please see the example notebook.

## TODO

* Validation
* Error handling
* Aliases

