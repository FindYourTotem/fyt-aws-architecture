# Continuous Integration / Continuous Delivery (CI/CD) Pipeline

We currently have two repositories that are automatically sent to S3.

In order to do this, we leveraged two AWS Developer Tools, CodeBuild and CodePipeline, in order to implement a CI/CD pipeline.

## Step 1: CodeBuild

We will use CodeBuild in order to automatically compile/build our code. Go to the [CodeBuild Homepage](https://console.aws.amazon.com/codesuite/codebuild/home) and select "Create Project".

Next, fill in the following information to create a build project.
* Project name
* Source
  * Source provider: GitHub
  * Repository: FindYourTotem/fyt-website-react
* Environment
  * Managed image
    * Operating system: Ubuntu
    * Runtime: Node.js
    * Runtime version: aws/codebuild/nodejs:10.1.0
    * Image version: Always use the latest image for this runtime version
  * Service role: New service role
* Buildspec
  * Build specifications: Use a buildspec file
    * We will insert in a buildspec.yml file into the base directory of the repository.
* Artifacts
  * Type: No artifacts
    * Normally we would use this to upload the "compiled" files to S3, but I had trouble configuring the file structure so that it's appropriate for the website. In this case, I found it easier to run a `aws s3 sync --delete build/` post_build command within the buildspec.yml file that does the upload instead of the Artifact step within CodeBuild.
    * Note: Since we are using an aws s3 sync command, we also have to give the service role created above permission to modify the S3 bucket. After the project and service role is created, find your service role [here](https://console.aws.amazon.com/iam/home?#/roles), and attach the "AmazonS3FullAccess" policy to your newly created service role.

After we create a CodeBuild project, we create a buildspec.yml file and place it into the base directory of the repository. This provides directions to CodeBuild on how to build the project. An example file would be something like:

```
version: 0.2
phases:
 install:
   commands:
     - echo "install step"
     - npm install
 pre_build:
   commands:
     - echo "pre_build step"
 build:
   commands:
     - npm run build
 post_build:
   commands:
     - echo "post_build step"
     - aws s3 sync --delete build/ s3://fytwebsitereact-20181023065530--hostingbucket/
```

The different ways you can configure the buildspec.yml file can be found in the [documentation here](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html).

## Step 2: CodePipeline

Now that you created and tested the CodeBuild project to see that it works, we automate the CodeBuild project through CodePipeline. This is where we set up our continuous delivery service, so that every time a change is merged to the master branch, we execute the CodeBuild project.

Go to the [CodePipeline homepage](https://console.aws.amazon.com/codesuite/codepipeline/pipelines) and select "Create pipeline".

Next, fill in the following information to create a CodePipeline project:

* Pipeline name
* Service role: New service role
* Artifact store: Default location
* Source provider: GitHub
  * Connect to GitHub and select the "FindYourTotem/fyt-website-react" repository
  * Branch: master
  * Change detection options: GitHub webhooks
    * This will setup a webhook so that CodePipeline would be notified when changes are made to the master branch.
* Build provider:
  * AWS CodeBuild
    * Project name: Name of the above CodeBuild project.
* Deploy
  * Skip
    * We don't really have a "deploy" stage for our project (since we technically "deployed" our project after moving the files to S3). This stage is normally used for projects where you also have to run/execute the code you build somewhere (for example, for a docker image project, you would build and upload the docker image through CodeBuild, and then you'd run and execute the image through CodeDeploy).
* Review settings and select "Create Pipeline"

This should create your pipeline, and any changes merged to the master branch will execute the CodePipeline, which would execute the CodeBuild project that will upload the project to S3.
