#!/usr/bin/env python3

import censys.certificates
import censys.ipv4
import censys
import sys
import cli
import os
import time
import os.path
from os import path
import socket

# Finds subdomains of a domain using Censys API
def find_subdomains(domain, api_id, api_secret):
    try:
        censys_certificates = censys.certificates.CensysCertificates(api_id=api_id, api_secret=api_secret)
        certificate_query = 'parsed.names: %s' % domain
        certificates_search_results = censys_certificates.search(certificate_query, fields=['parsed.names'])
        
        # Flatten the result, and remove duplicates
        subdomains = []
        for search_result in certificates_search_results:
            subdomains.extend(search_result['parsed.names'])
		
        return set(subdomains)
    except censys.base.CensysUnauthorizedException:
        sys.stderr.write('[-] Your Censys credentials look invalid.\n')
        exit(1)
    except censys.base.CensysRateLimitExceededException:
        sys.stderr.write('[-] Looks like you exceeded your Censys account limits rate. Exiting\n')
        return set(subdomains)
    except censys.base.CensysException as e:
        # catch the Censys Base exception, example "only 1000 first results are available"
        sys.stderr.write('[-] Something bad happened, ' + repr(e))
        return set(subdomains)

# Filters out uninteresting subdomains
def filter_subdomains(domain, subdomains):
	return [ subdomain for subdomain in subdomains if '*' not in subdomain and subdomain.endswith(domain) ]

# Prints the list of found subdomains to stdout
def print_subdomains(domain, subdomains, time_ellapsed):
    if len(subdomains) is 0:
        print('[-] Did not find any subdomain')
        return

    print('[*] Found %d unique subdomain%s of %s in ~%s seconds\n' % (len(subdomains), 's' if len(subdomains) > 1 else '', domain, str(time_ellapsed)))
    for subdomain in subdomains:
        print('  - ' + subdomain)
    
    print('')

# Saves the list of found subdomains to an output file
def save_subdomains_to_file(subdomains, output_file):
    if output_file is None or len(subdomains) is 0:
        return

    try:
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(subdomain + '\n')

        print('[*] Wrote %d subdomains to %s' % (len(subdomains), os.path.abspath(output_file)))
    except IOError as e:
        sys.stderr.write('[-] Unable to write to output file %s : %s\n' % (output_file, e))

def main(domain, output_file, censys_api_id, censys_api_secret):
    print('[*] Searching Censys for subdomains of %s' % domain)
    start_time = time.time()
    subdomains = find_subdomains(domain, censys_api_id, censys_api_secret)
    subdomains = filter_subdomains(domain, subdomains)
    end_time = time.time()
    time_ellapsed = round(end_time - start_time, 1)
    print_subdomains(domain, subdomains, time_ellapsed)
    save_subdomains_to_file(subdomains, output_file)
    return subdomains

def get_subdomains_for_api(domain):
    censys_api_id = "44ea4a45-31ef-4b45-b0b6-0e60e0dd830d"
    censys_api_secret = "fWRdn2hoExraAmwcxrDuqrFogQ8UXeah"
    output_file = domain + ".txt"
    
    if path.exists(output_file):
        f = open(output_file, "r")
        data = f.readlines()
        subdomain_list = [x.strip() for x in data] 
    else:
        subdomain_list = main(domain, output_file, censys_api_id, censys_api_secret)
    return subdomain_list

def get_subdomain_details(subdomain_hostnames):
    subdomain_list = []
    
    for subdomain_hostname in subdomain_hostnames:
        print(subdomain_hostname)
        subdomain_ip = socket.gethostbyname(subdomain_hostname)
        subdomain = {}
        subdomain["hostname"] = subdomain_hostname
        subdomain["ip"] = subdomain_ip
        subdomain_list.append(subdomain)
    return subdomain_list

if __name__ == "__main__":

    subdomain_names = get_subdomains_for_api("test.com")
    print(subdomain_names)
    # print(get_subdomain_details(subdomain_names))

    # args = cli.parser.parse_args()

    # censys_api_id = "44ea4a45-31ef-4b45-b0b6-0e60e0dd830d"
    # censys_api_secret = "fWRdn2hoExraAmwcxrDuqrFogQ8UXeah"

    # if 'CENSYS_API_ID' in os.environ and 'CENSYS_API_SECRET' in os.environ:
    #     censys_api_id = os.environ['CENSYS_API_ID']
    #     censys_api_secret = os.environ['CENSYS_API_SECRET']

    # if args.censys_api_id and args.censys_api_secret:
    #     censys_api_id = args.censys_api_id
    #     censys_api_secret = args.censys_api_secret

    # if None in [ censys_api_id, censys_api_secret ]:
    #     sys.stderr.write('[!] Please set your Censys API ID and secret from your environment (CENSYS_API_ID and CENSYS_API_SECRET) or from the command line.\n')
    #     exit(1)
		
    # main(args.domain, args.output_file, censys_api_id, censys_api_secret)
