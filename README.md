# mercadinho

Imagine you could take a picture of a product you often buy in a supermarket and see what's it price in every supermarket around you. Wouldn't that be nice?

Well, we have to start by digitizing all the information in the receipt. This is just a quick test I did to see how easy would it be to extract all the products information (SKU, description, price) and store information (address, name, location) from a picture of the receipt. It turns out it is quite easy just using [Google Vision OCR](https://cloud.google.com/vision/docs/ocr) and [Open AI structured outputs](https://platform.openai.com/docs/guides/structured-outputs).

On the `receipt` folder there is a simple flask app that receives a (Brazilian for now) receipt and returns a JSON with all the information.
There is a `tests` folders that contains some receipts images to test it with.
