import boto3
from botocore.exceptions import ClientError


def get_or_create_glossary(domain_id, glossary_name, glossary_description='', profile_name='default', region_name='ap-southeast-2'):

    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    datazone = session.client('datazone')

    # Check for existing glossary
    try:
        response = datazone.list_glossaries(domainIdentifier=domain_id)
        for glossary in response.get('items', []):
            if glossary.get('name') == glossary_name:
                print(f"[ℹ] Glossary '{glossary_name}' already exists with ID: {glossary.get('id')}")
                return glossary.get('id')
    except ClientError as e:
        print(f"[⚠️] Could not list glossaries: {e}")
    except Exception as e:
        print(f"[⚠️] Unexpected error listing glossaries: {e}")

    # Create glossary
    try:
        response = datazone.create_glossary(
            domainIdentifier=domain_id,
            name=glossary_name,
            shortDescription=glossary_description
        )
        glossary_id = response['id']
        print(f"[✔] Glossary '{glossary_name}' created with ID: {glossary_id}")
        return glossary_id
    except ClientError as e:
        print(f"[❌] Failed to create glossary: {e}")
    except Exception as e:
        print(f"[❌] Unexpected error creating glossary: {e}")

    return None



def get_or_create_glossary_term(domain_id, glossary_id, term_name, term_description='', profile_name='default', region_name='ap-southeast-2'):

    session = boto3.Session(profile_name=profile_name, region_name=region_name)
    datazone = session.client('datazone')

    # Try listing existing terms
    try:
        response = datazone.list_glossary_terms(
            domainIdentifier=domain_id,
            glossaryIdentifier=glossary_id
        )
        for term in response.get('items', []):
            if term.get('name') == term_name:
                print(f"[ℹ] Glossary term '{term_name}' already exists with ID: {term.get('id')}")
                return term.get('id')
    except ClientError as e:
        print(f"[⚠️] Could not list glossary terms: {e}")
    except Exception as e:
        print(f"[⚠️] Unexpected error listing glossary terms: {e}")

    # Try creating the term
    try:
        response = datazone.create_glossary_term(
            domainIdentifier=domain_id,
            glossaryIdentifier=glossary_id,
            name=term_name,
            shortDescription=term_description
        )
        term_id = response['id']
        print(f"[✔] Glossary term '{term_name}' created with ID: {term_id}")
        return term_id
    except ClientError as e:
        print(f"[❌] Failed to create glossary term: {e}")
    except Exception as e:
        print(f"[❌] Unexpected error creating glossary term: {e}")

    return None


