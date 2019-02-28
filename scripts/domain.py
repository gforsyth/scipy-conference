from load_save import load_rev_sublist, save_rev_sublist
import pandas


def domain_pool_subs(sublist):

    domains = set()
    for sub in sublist:
        domains.add(sub.domain)

    domain_pool = dict()
    for domain in domains:
        domain_pool[domain] = []

    for sub in sublist:
        domain_pool[sub.domain].append(sub)

    return domain_pool
