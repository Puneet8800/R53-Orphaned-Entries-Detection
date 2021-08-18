### Purpose
 The purpose of this automation is to detects all the AWS Route53 orphaned entries, it will prevent from hijacking the subdomain of an aws account.

### Deployment Options
AWS Lambda, Rundeck or any cron

### Prerequisites
1. IAM role with a permission cloudfront, loadbalancer, elastic cache, rds in read only.

### Configuration Steps
1. Configure IAM role with permission mention above in prerequisites.
2. Deploy it on any of the cron Lambda/rundeck.



### References
1. IAM https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_change-permissions.html
