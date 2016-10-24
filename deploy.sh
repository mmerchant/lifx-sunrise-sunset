#!/bin/bash
CWD=$(pwd)
LAMBDA_FX_NAME="lifx-sunrise-sunset"
if [ -f "$CWD/lifx-deployment-pkg.zip" ]
then
    rm "$CWD/lifx-deployment-pkg.zip"
fi
echo "Adding Python files..."
zip -r9 "$CWD/lifx-deployment-pkg.zip" ./*.py
sleep 1
echo "------------------------------------------"
echo "Adding site packages..."
cd "$VIRTUAL_ENV"/lib/python2.7/site-packages/ || exit
zip -r9 "$CWD/lifx-deployment-pkg.zip" ./*
pwd
cd "$CWD" || exit
sleep 1
echo "------------------------------------------"
echo "Deploying to AWS Lambda..."
aws lambda update-function-code --function-name "$LAMBDA_FX_NAME" \
    --zip-file fileb://lifx-deployment-pkg.zip
aws lambda update-function-configuration --function-name  "$LAMBDA_FX_NAME" \
    --description 'Enforce Lifx follow sunrise/sunset schedules.' \
    --handler 'enforce-lifx-sunrise-sunset.lambda_handler'
echo "Updated Lambda functions..."
rm "$CWD/lifx-deployment-pkg.zip"