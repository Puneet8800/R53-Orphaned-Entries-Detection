import sys
import argparse
import re
import boto3
import json
import re
import requests

session = boto3.Session(profile_name='profile_name')
boto3.setup_default_session(profile_name='profile_name')
def ip(Ip):
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'''
    if(re.search(regex, Ip)):
        return True  
    else:  
        return False
def load_balancer():
    loadbalancer = []
    lbs = boto3.client('elb',region_name='us-east-1')
    lb_paginator = lbs.get_paginator('describe_load_balancers')
    lb_page_iterator = lb_paginator.paginate()  
    for page in lb_page_iterator:
        for alb in page['LoadBalancerDescriptions']:
            loadbalancer.append(alb['DNSName'])
    lbs = boto3.client('elbv2',region_name='us-east-1')
    lb_paginator = lbs.get_paginator('describe_load_balancers')
    lb_page_iterator = lb_paginator.paginate()  
    for page in lb_page_iterator:
        for alb in page['LoadBalancers']:
            loadbalancer.append(alb['DNSName'])
    return loadbalancer
def cloudfront():
    cloudfront =[]
    cf = boto3.client('cloudfront')
    cf_paginator = cf.get_paginator('list_distributions')
    cf_page_iterator = cf_paginator.paginate()
    for page in cf_page_iterator:
        if page['DistributionList']['Quantity'] > 0:
            for i in page['DistributionList']['Items']:
                cloudfront.append(i['DomainName'])
    return cloudfront



def rds():
    r=[]
    rds = boto3.client('rds',region_name='us-east-1')
    rds_paginator = rds.get_paginator('describe_db_cluster_endpoints')
    rds_page_iterator = rds_paginator.paginate()  
    for page in rds_page_iterator:
        for rds in page['DBClusterEndpoints']:
            r.append(rds['Endpoint'])
    return r    

def get_route53_A_record():
    d={}
    r53 = boto3.client('route53')
    r53_paginator = r53.get_paginator('list_resource_record_sets')
    r53_page_iterator = r53_paginator.paginate(HostedZoneId='put_hosted_zone_id')
    for page in r53_page_iterator:
        for i in page['ResourceRecordSets']:
            if i['Type'] == 'A':
                if 'ResourceRecords' in i:
                    for j in i['ResourceRecords']:
                            z= j['Value']
                            if z.endswith('.'):
                                d[z[:-1]] = i['Name']
                            else:
                                d[z] = i['Name']
                if 'AliasTarget' in i:
                    s = i['AliasTarget']['DNSName']
                    if s.endswith('.'):
                        d[z[:-1]] = i['Name']
                    else:
                        d[z] = i['Name']
            if i['Type'] == 'CNAME':
                if 'ResourceRecords' in i:
                    for j in i['ResourceRecords']:
                        z= j['Value']
                        d[z] = i['Name']
                if 'AliasTarget' in i:
                    s = i['AliasTarget']['DNSName']
                    d[s] = i['Name']
    return(d)
def cache():
    c=[]
    rds = boto3.client('elasticache',region_name='us-east-1')
    rds_paginator = rds.get_paginator('describe_cache_clusters')
    rds_page_iterator = rds_paginator.paginate()  
    for page in rds_page_iterator:
        for rds in page['CacheClusters']:
            if 'ReplicationGroupId' in rds:
                c.append(rds['ReplicationGroupId']+'.xxxxxxx.cache.amazonaws.com')
                c.append(rds['CacheClusterId']+'.xxxxxx.cache.amazonaws.com')
            else:
                c.append(rds['CacheClusterId']+'.xxxxxxx.cache.amazonaws.com')
    return c


def main():
    #e=ec2()
    
    cf= cloudfront()
    lb= load_balancer()
    r = rds()
    r53 = get_route53_A_record()
    c= cache()
    template = {}
    template['attachments'] = [{}]
    template['attachments'][0]['fallback'] = 'unable to display this message !'
    template['attachments'][0]['color'] = '#36a64f'
    template['attachments'][0]['pretext'] = "Orphaned Route53 entries"
    template['attachments'][0]['title'] = "env"
    template['attachments'][0]['fields'] = [{"title": "Entries can be deleted "}]
    cf1= {}
    load= {}
    cache1={}
    rds1 = {}
    for i,j in r53.items():

        if i.endswith('cloudfront.net'):
            if i not in cf:
                #print(i + " : " + j)
                cf1[i]=j
                
        elif i.endswith('elb.amazonaws.com'):
            if i not in lb:
                #print(i + " : " + j)
                load[i] = j
        elif i.endswith('rds.amazonaws.com'):
            if i not in r:
                #print(i + " : " + j)
                rds1[i] = j
        if i.endswith('cache.amazonaws.com'):
            if i not in c:
                #print(i + " : " + j)
                cache1[i] = j
    template = {}
    template['attachments'] = [{}]
    template['attachments'][0]['fallback'] = 'unable to display this message !'
    template['attachments'][0]['color'] = '#36a64f'
    template['attachments'][0]['pretext'] = "Orphaned Route53 entries"
    template['attachments'][0]['title'] = "Env"
    template['attachments'][0]['fields'] = [{"title": "Cloudfront "}]
    for i,j in cf1.items():
        template['attachments'][0]['fields'].append({"value": i + " : " + j})
    json_template = json.dumps(template)
    requests.post(url='slack incoming webhook url', data=json_template)
    template = {}
    template['attachments'] = [{}]
    template['attachments'][0]['fallback'] = 'unable to display this message !'
    template['attachments'][0]['color'] = '#36a64f'
    template['attachments'][0]['pretext'] = "Orphaned Route53 entries"
    template['attachments'][0]['title'] = "env"
    template['attachments'][0]['fields'] = [{"title": "Loadbalancer "}]
    
    for i,j in load.items():
        template['attachments'][0]['fields'].append({"value": i + " : " + j})
    json_template = json.dumps(template)
    requests.post(url='slack incoming webhook url', data=json_template)

    template = {}
    template['attachments'] = [{}]
    template['attachments'][0]['fallback'] = 'unable to display this message !'
    template['attachments'][0]['color'] = '#36a64f'
    template['attachments'][0]['pretext'] = "Orphaned Route53 entries"
    template['attachments'][0]['title'] = "env"
    template['attachments'][0]['fields'] = [{"title": "RDS"}]
    for i,j in rds1.items():
        template['attachments'][0]['fields'].append({"value": i + " : " + j})
    json_template = json.dumps(template)
    requests.post(url='slack incoming webhook url', data=json_template)
    template = {}
    template['attachments'] = [{}]
    template['attachments'][0]['fallback'] = 'unable to display this message !'
    template['attachments'][0]['color'] = '#36a64f'
    template['attachments'][0]['pretext'] = "Orphaned Route53 entries"
    template['attachments'][0]['title'] = "env"
    template['attachments'][0]['fields'] = [{"title": "Elastic Cache"}]
    for i,j in cache1.items():
        template['attachments'][0]['fields'].append({"value": i + " : " + j})
        
    json_template = json.dumps(template)
    requests.post(url='slack incoming webhook url', data=json_template)
    



if __name__ == '__main__':
    main()
