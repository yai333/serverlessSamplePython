# Introduction
This is an example of AWS StepFunctions workflow building by Serverless Framework python template.

![Diagram](BillyWorkshop-sepfunction-dynamodb-s3.png)

# Install Serverless Framework

Before getting started, Install the Serverless Framework. Open up a terminal and type `npm install -g serverless` to install Serverless framework.

# Create a new service
Create a new service using the AWS Python template, specifying a unique name and an optional path.

```
$sls create --template aws-python --path eventdatapipeline
```
After project generated, In the app folder, there is a `serverless.yml` file. This file is needed to configure how our application will behave.

# Install Serverless Plugin

Then can run the following command project root directory to install required plugins

## Serverless Python requirement
Serverless plugin to bundle Python packages
```
$ sls plugin install -n serverless-python-requirements

```
## Serverless Offline Python/Ruby Plugin
Emulate AWS λ and API Gateway locally when developing your Serverless project.
```
$ npm install serverless-offline-python --save-dev
```

## Serverless AWS Pseudo Parameters
Use the CloudFormation Pseudo Parameters in your `serverless.yml`.
```
$ npm install serverless-pseudo-parameters
```

## Serverless Step Functions
```
$ npm install --save-dev serverless-step-functions
```

Edit the serverless.yml file to look like the following:

```
plugins:
  - serverless-python-requirements
  - serverless-plugin-tracing
  - serverless-pseudo-parameters
  - serverless-offline-python
  - serverless-step-functions

custom:
  pythonRequirements:
    layer: false #Put dependencies into a Lambda Layer.  

```  

# Configure API key for API Gateway

Please note that those are the API keys names, not the actual values. Once you deploy your service, the value of those API keys will be auto generated by AWS and printed on the screen for you to use. The values can be concealed from the output with the --conceal deploy option.

Clients connecting to this Rest API will then need to set any of these API keys values in the x-api-key header of their request.

```
provider:
  apiKeys:
    - myFirstKey
    - ${opt:stage}-myFirstKey
```  

# S3 CloudFormation Resources

Add S3 resource to `resources` section in `serverless.yml`

```
resources:
  Resource:
    S3BucketEvent:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:custom.activityBucket}

```

# DynamoDB CloudFormation Resources

```
resources:
  Resource:
    ActivityTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.activityTable}
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
          - AttributeName: date
            AttributeType: S
          - AttributeName: location
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
          - AttributeName: date
            KeyType: RANGE
        LocalSecondaryIndexes:
          - IndexName: locationIndex
            KeySchema:
              - AttributeName: id
                KeyType: HASH
              - AttributeName: location
                KeyType: RANGE
            Projection:
              ProjectionType: ALL
        ProvisionedThroughput:
          ReadCapacityUnits: ${self:custom.tableThroughputs.${self:provider.stage}}
          WriteCapacityUnits: ${self:custom.tableThroughputs.${self:provider.stage}}
        StreamSpecification:
          StreamViewType: NEW_IMAGE
```

# StepFunction Resources

Add following StepFunction configs to `stepFunctions` section in `serverless.yml`
```
stepFunctions:
  stateMachines:
    eventsActivitiesProcess:
      name: eventsActivitiesProcess-${opt:stage}
      definition:
        Comment: "Sync data from dynamodb to S3, caculate insight by type"
        StartAt: parallelMessageProcessing
        States:
          parallelMessageProcessing:
            Type: Parallel
            Branches:
              - StartAt: validateMessage
                States:
                  validateMessage:
                    Type: Choice
                    Choices:
                      - Variable: $.location
                        StringEquals: "Bathroom"
                        Next: caculateInsightOne
                      - Variable: $.location
                        StringEquals: "Kitchen"
                        Next: caculateInsightTwo
                    Default: defaultState
                  caculateInsightOne:
                    Type: Task
                    Resource: arn:aws:lambda:${self:provider.region}:#{AWS::AccountId}:function:${self:service}-${opt:stage}-caculateInsightOne
                    End: true
                  caculateInsightTwo:
                    Type: Task
                    Resource: arn:aws:lambda:${self:provider.region}:#{AWS::AccountId}:function:${self:service}-${opt:stage}-caculateInsightTwo
                    End: true
                  defaultState:
                    Type: Succeed
              - StartAt: syncDBToS3
                States:
                  syncDBToS3:
                    Type: Task
                    Resource: arn:aws:lambda:${self:provider.region}:#{AWS::AccountId}:function:${self:service}-${opt:stage}-syncDBToS3
                    End: true
            End: true
```

# Lambda Resources
Add following StepFunction configs to `functions` section in `serverless.yml`

```
functions:
  addNewEventMessage:
    handler: handler.addNewEventMessage
    events:
      - http:
          path: message/event
          method: put
          private: true
  addNewActivityMessage:
    handler: handler.addNewActivityMessage
    events:
      - http:
          path: message/activity
          method: put
          private: true
  newMessageEventListener:
    handler: handler.newMessageEventListener
    environment:
      statemachineArn: ${self:resources.Outputs.EventsActivitiesProcess.Value}
    events:
      - stream:
          type: dynamodb
          arn:
            Fn::GetAtt: [EventTable, StreamArn]
      - stream:
          type: dynamodb
          arn:
            Fn::GetAtt: [ActivityTable, StreamArn]
  caculateInsightOne:
    handler: handler.caculateInsightOne
  caculateInsightTwo:
    handler: handler.caculateInsightTwo
  syncDBToS3:
    handler: handler.syncDBToS3

```

# Lambda function
Lambda functions are in `handler.py`.

# Deploy
Once you deploy your service, the value of those API keys will be auto generated by AWS and printed on the screen for you to use. The values can be concealed from the output with the --conceal deploy option.
```
sls deploy --stage dev --region YOUR-REGION
```
