Here is a standard README for the vcon-right-to-know repository:

# vcon-right-to-know

vcon-right-to-know is a Python demo that allows users to request information from companies about the personal data they have collected.

## Overview

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

## Installation and Usage

1. Clone the repository:

```
git clone https://github.com/vcon-dev/vcon-right-to-know.git
```

2. Create a new virtual environment (optional):

``` 
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Make a new secrets.toml file inside ~/.streamlit. This is the S3 bucket which will contain the vCons that will be searched for this demonstration. This is a demo, and will load all of the vCons from the S3 bucket.
```
S3_BUCKET = "fake-vcons"
AWS_ACCESS_KEY = "AK**************"
AWS_SECRET_KEY = "Xl**************"
```
5. Run streamlit
```
streamlit run right-to-know.py
```

## Contributing

Contributions are welcome! Please follow the guidelines in CONTRIBUTING.md.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
