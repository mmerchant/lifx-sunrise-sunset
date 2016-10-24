# lifx-sunrise-sunset
---------------------
So I use Lifx but every now and then the sunrise/sunset scheduler doesn't work.
This Lambda package will run on a scheduler and just enforce it.

Enforce via AWS Lambda your Lifx bulb is following sunrise/sunset schedules.
If there is a correction made, it will notify you via SMS using Flowroute's API.

### Installation:
- Create a Lambda function in your AWS account.
- Update `LAMBDA_FX_NAME` in deploy.sh to the updated name of your Lambda function.
- Create a virtualenv and activate it.
- Install the files from requirements (pip install -r requirements.txt)
- Add your API keys, phone numbers, and location in the lambda function.
- Run the deploy.sh script

### Attributions:
- Sunrise-Sunset [http://sunrise-sunset.org/]

### TODO:
- Tests
- Exception handling