#!/usr/bin/env python3
"""Script to make a Client to be an admin"""

import argparse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.client import Client
from models.basemodel import DATABASE_URI

# Set up argument parser
parser = argparse.ArgumentParser(description='Make a client an admin.')
parser.add_argument('client_id', type=str,
                    help='The ID of the client to be made admin')
args = parser.parse_args()

engine = create_engine(DATABASE_URI)

# Create a configured session
Session = sessionmaker(bind=engine)
session = Session()

# Make client with specific id an admin
client_id = args.client_id
client = session.query(Client).filter_by(public_id=client_id).first()
if client:
    client.role = 'admin'
    session.commit()
    print(f"Client with ID {client_id} has been made an admin.")
else:
    print(f"Client with ID {client_id} not found.")
