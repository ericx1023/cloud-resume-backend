# Cloud Resume - AWS

This project is a complete implementation of the [Cloud Resume](https://cloudresumechallenge.dev/docs/the-challenge/aws/), which also demonstrate AWS cloud skills.

## Project Architecture

The project is divided into the following main components:

### Frontend
- Personal resume website created using HTML, CSS, and JavaScript
- Hosted as a static website on Amazon S3
- HTTPS enabled through CloudFront
- Accessible via a custom domain name through Route 53

### Backend
- Serverless API using API Gateway and Lambda functions
- Python Lambda function to handle visitor count
- DynamoDB database to store visitor count
- Includes appropriate unit tests

### Infrastructure as Code
- All resources defined using AWS SAM (Serverless Application Model)
- Complete CI/CD pipeline implemented through GitHub Actions for automatic deployment

## Deployment Instructions

For detailed deployment guides, please refer to the [deployment.md](deployment.md) file.

## Learning Notes

Experience and learning notes from this project can be found on [my blog](https://example.com/blog-post). 