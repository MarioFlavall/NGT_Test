
# NGT Test Project

This project contains:

api.py - This is the file for the REST API used to interact with the data extracted from the files (AAPL.csv, FB.csv). 
This was running on my local machine via "python api.py" as I had not yet had time to set up the Cloud Run and make it production ready rather than the debug dev setup.

cloud_function.py - This is the file containing the code that I was using in the UI editor for the Google Cloud cloud_function

Overall, I would have definitely liked to spend some more time on security of the API. At the moment, it has a basic registration system (open and not ideal).

Would have definitely liked to have implemented proper testing and a CI/CD pipeline, it was something that I was not sure how to implement via the Google ecosystem and I was moreso distracted with trying to get all of the moving parts working.


