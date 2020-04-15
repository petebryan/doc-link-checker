# doc-link-checker
Doc Link Checker provides near real-time checking of URLs included in a GitHub project documentation 
and to enable alerting and response to any broken URLs.

This project is an Azure Function App that checks a folder of markdown docs from a GitHub repository
and identifies and URLs in the markdown. It then checks the current response code to requests for these
and if a 200 code is not received it sends a message to an Azure Event Hub stating which URL failed 
and what the response code received was.

In order to use this Azure Funtion App you will need a configured Event Hub and Azure Storage account.
You also need to set an Function App Application setting named 'docFolder' which contains the path to 
the top level documentation folder in the GitHub project.

To learn how to take this code and deploy it as an Azure Function using VSCode check out this 
documentation: https://docs.microsoft.com/en-us/azure/developer/python/tutorial-vs-code-serverless-python-01 

For details on how to deploy an Event Hub please refer to this documentation: 
https://docs.microsoft.com/en-us/azure/event-hubs/

This project is still a work in progress. Future plans include converting this into an ARM template to
deploy the Function App and Event Hub.
