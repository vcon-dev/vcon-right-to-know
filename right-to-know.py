import streamlit as st
import json
import boto3
import requests


S3_BUCKET = st.secrets["S3_BUCKET"]
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]

DATATRAILS_CLIENT = st.secrets["DATATRAILS_CLIENT"]
DATATRAILS_SECRET = st.secrets["DATATRAILS_SECRET"]

# Connect to the S3 bucket
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

@st.cache_data
def get_documents():
    # Retrieve all documents from an S3 Bucket, and 
    # return them as a list of dictionaries. vCons 
    # will have the suffix vcon.json
    documents = []
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    for obj in response['Contents']:
        if obj['Key'].endswith('.vcon.json'):
            document = s3.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
            documents.append(json.loads(document['Body'].read()))
    return documents
    

@st.cache_data
def get_token():
    import requests
    import os

    url = "https://app.datatrails.ai/archivist/iam/v1/appidp/token"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': DATATRAILS_CLIENT,
        'client_secret': DATATRAILS_SECRET
    }

    response = requests.post(url, headers=headers, data=data)
    print(response)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        
        # Assuming you want to store the token in an environment variable
        return response_json['access_token']
        
def search_documents(query):
    # Query the MongoDB collection for matching documents within the "parties" element
    # documents = collection.find({'parties': {'$elemMatch': {'$or': [{'mailto': query}, {'tel': query}]}}})
    #return list(documents)
    return [doc for doc in st.session_state.documents if any(query in party.get('mailto', '') or query in party.get('tel', '') for party in doc['parties'])]

def main():
    # Setup the session state to store the confirmation code
    if 'confirmation_code' not in st.session_state:
        st.session_state.confirmation_code = None
        st.session_state.state = "initial"
        st.session_state.query = None
        st.session_state.documents = get_documents()

    confirming = False
    sending_code = False

    st.title('Right to Know, Right to Erasure')
    st.subheader('Request Access or Deletion of Personal Data')

    if st.session_state.state == "initial":
        st.markdown("""
                    Thank you for being a customer of Spacely Sprockets.  We take your privacy seriously and are committed to
                    protecting your personal data.  If you would like to request access to your personal data, or if you would
                    like to request the deletion of your personal data
                    
                    - Please enter your email or phone number below.  
                    - We will send you a confirmation code to that phone number or email address 
                    - Enter that code in the confirmation code box, and click the "Confirm" button.
                    - We will then send you a link to download your personal data or to confirm the deletion of your personal data.

                    """)

    st.sidebar.title('ABOUT THIS APP')
    st.sidebar.markdown("""
                    ## Abstract
                        
                    This app allows a consumer to request access to their personal data from an organization,
                    or to request the deletion of their personal data. The app searches for matching documents
                    in a MongoDB collection of vCons (virtual conversations). The user can enter an email or 
                    phone number to search for matching documents.

                    ## Relevant Rights
                        
                    Customer data privacy is a fundamental right. Although many countries have privacy laws,
                    the European Union has some of the most comprehensive data protection laws. Two key rights
                    are the Right to be Forgotten and the Right to Access.
                        
                    **The Right to be Forgotten**, also known as the Right to Erasure, is enshrined in the 
                    General Data Protection Regulation (GDPR) of the European Union. It allows individuals 
                    to request the deletion of their personal data by an organization under certain 
                    conditions. This right is particularly relevant when the data is no longer 
                    necessary for the purposes for which it was collected, the individual withdraws 
                    consent, or the data has been unlawfully processed.

                    **The Right to Access**, on the other hand, empowers individuals to request access 
                    to their personal data from an organization. This includes the right to know whether 
                    their personal data is being processed, what data is being processed, and for what purpose. 
                    Organizations must provide a copy of the personal data, free of charge, in an electronic 
                    format if requested. This right ensures transparency and allows individuals to verify the 
                    lawfulness of the processing.
                    """)
    st.sidebar.json(st.session_state.documents)

    # User input
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.state == "initial":
            query = st.text_input('Enter an email or phone number:')
            sending_code = st.button('Send Confirmation Code')
        if st.session_state.state == "confirmation_code_sent":
            confirmation_code = st.text_input('Enter confirmation code:')
            confirming = st.button('Confirm')


            

    if sending_code:
        # Check to see if there's a valid email or phone number.
        # phone number is valid if it starts with a + and is followed by 11 digits
        if '@' in query or query.startswith('+') and query[1:].isdigit() and len(query) == 12:
            st.session_state.confirmation_code_sent = True
        else:
            st.error('Please enter a valid email or phone number.')
            st.stop()

        # Send confirmation code
        st.session_state.confirmation_code = '123456'
        st.session_state.state = "confirmation_code_sent"
        st.session_state.query = query

        # Rerun the app to display the confirmation code input
        st.rerun()


    if confirming:
        if confirmation_code == st.session_state.confirmation_code:
            st.success('Confirmation code verified.')
            st.session_state.state = "confirmed"
            st.rerun()
        else:
            st.error('Invalid confirmation code.')
            st.stop()
    
    if st.session_state.state == "confirmed":
        # Search for matching documents
        if st.session_state.documents:
            st.title('Results')

            st.subheader('Access History')
            token = get_token()
            assett_uuid = "6edf0ce4-0701-465d-b7c0-7f8b69f7807d"
            url = f"https://app.datatrails.ai/archivist/v2/assets/{assett_uuid}/events"
            authorization = f"Bearer {token}"

            payload = {}
            headers = {
                'Authorization': authorization
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code is not 200:
                st.error(f"Error: {response.status_code}")


            st.subheader('Summary')
            st.markdown("""
                        The following documents contain your email or phone number. 
                        You can request access to these documents or request the deletion of your personal data.
                        """)    
            
            # Display the matching documents
            matching_documents = search_documents(st.session_state.query)
            for doc in matching_documents:
                st.markdown("## Conversation ")
                col1, col2 = st.columns(2)
                with col1:
                    # For each vCon, display the created_at, parties, summary (if available) and the link to the document
                    st.markdown(f"""
                                **Created At:** {doc['created_at']}

                                **Parties:** {', '.join([party['name'] for party in doc['parties']])}

                                """)
                    if 'summary' in doc:
                        st.write(doc['summary'])
                    else:
                        st.write('No summary available.')

                with col2:
                    # Make a download button to download the document
                    st.download_button(
                        label='Download Conversation',
                        data=json.dumps(doc, indent=4),
                        file_name=doc['uuid'] + '.vcon.json',
                        mime='application/json'
                    )
                    delete = st.button('Delete', key=doc['uuid']+":delete")
                    if delete:
                        st.info(f'Deleting {doc["uuid"]}...')
                        # Delete the document from the S3 bucket
                        s3.delete_object(Bucket=S3_BUCKET, Key=doc['uuid'] + '.vcon.json')

                        # Remove the document from the session state
                        st.session_state.documents.remove(doc)
                        st.toast(f'{doc["uuid"]} deleted.')
                        
                        # Reset the state to initial
                        st.session_state.state = "initial"
                        st.session_state.query = None
                        st.session_state.confirmation_code = None
                        st.session_state.confirmation_code_sent = False
                        st.rerun()


                st.markdown('---')
                # Display the full document in JSON format if the user clicks the "Show JSON" button
                if st.button('Show vCon', key=doc['uuid']):
                    st.json(doc, expanded=False)
                    
            # Display the access history
            events = response.json()['events']

            st.subheader('Access History')
            # Display the access history in a table
            for event in events:
                # Check to make sure that the event attributes are not empty
                required_attributes = ['issuer', 'subject', 'action', 'hash']
                if not all(attr in event['event_attributes'] for attr in required_attributes):
                    continue
                
                st.markdown('---')
                event_attributes = event['event_attributes']
                st.write(f"Issued by: {event_attributes['issuer']}")
                st.write(f"Issued at: {event['timestamp_declared']}")
                st.write(f"Confirmation Status: {event['confirmation_status']}")
                st.write(f"Subject: {event_attributes['subject']}")
                st.write(f"Action: {event_attributes['action']}")
                st.write(f"Hash: {event_attributes['hash']}")

        else:
            st.info('No matching documents found.')

if __name__ == '__main__':
    main()