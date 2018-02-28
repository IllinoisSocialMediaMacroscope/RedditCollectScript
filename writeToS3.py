''' helper function to interact with aws S3 bucket: macroscope-smile
    use AWS role instead of access key and access token
'''
import os
import requests
import boto3


client = boto3.client('s3')
bucketName = 'reddit-comment-macroscope'

# upload local file to s3 with a specied remote path
def upload(localPath, remotePath, filename):
    client.upload_file(os.path.join(localPath, filename),
                       bucketName,
                       os.path.join(remotePath, filename))

# create directory in s3 bucket
# directoryName must end with a slash
def createDirectory(directoryName):
    client.put_object(Bucket=bucketName, Key=directoryName)
   
# given s3 path and filename,
# generate downloadable URL with temp credentials
def generate_downloads(remotePath, filename):
    url = client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucketName,
                    'Key': os.path.join(remotePath, filename)
                },
                ExpiresIn=604800  # one week
    )

    return url

# given s3 path and filename,
# download remote file to specified path of local disk 
def downloadToDisk(filename, localPath, remotePath):
    with open(os.path.join(localPath, filename), 'wb') as f:
        client.download_fileobj(bucketName,
                                os.path.join(remotePath, filename), f)

# given remote key (path + filename)
# read this file content into a python object
def getObject(remoteKey):
    obj = client.get_object(Bucket=bucketName, Key=remoteKey)

# directly write python object to a remote file
def putObject(body, remoteKey):
    # bytes or seekable file-like object
    obj = client.put_object(Bucket=bucketName,
                            Body=body, 
                            Key=remoteKey)
   
# check if a file exist in s3
def checkExist(remotePath, filename):
    t = client.head_object(Bucket=bucketName,
                           Key=os.path.join(remotePath, filename))

# list Directory in s3 given a path
def listDir(remotePath):
    objects = client.list_objects(Bucket=bucketName,
                                  Prefix=remotePath,
                                  Delimiter='/')
    folderNames = []
    for o in objects.get('CommonPrefixes'):
        folderNames.append(o.get('Prefix'))
    
    return folderNames

# list Files in s3 given a path
# return rich information about the files
def listFiles(remotePath):
    objects = client.list_objects(Bucket=bucketName,
                                  Prefix=remotePath)
    
    return objects.get('Contents')
