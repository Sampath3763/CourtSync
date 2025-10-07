#!/usr/bin/env python3
"""
One-time database data clearing script
This will clear all user sessions, documents, and rooms from the database
Run this whenever you need to reset the database data to a clean state.

Usage:
    python clear_db_data.py
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Room, Document

def clear_database_data():
    """Clear all data from database tables while keeping the schema."""
    print("🗑️  Clearing database data...")
    
    # Create the Flask app
    app = create_app('development')
    
    with app.app_context():
        try:
            # Count existing records
            user_count = db.session.query(User).count()
            document_count = db.session.query(Document).count()
            room_count = db.session.query(Room).count()
            
            print(f"Found: {user_count} users, {document_count} documents, {room_count} rooms")
            
            if user_count == 0 and document_count == 0 and room_count == 0:
                print("Database is already empty!")
                return
            
            # Confirm before clearing
            print("\nThis will permanently delete ALL data from the database!")
            confirm = input("Are you sure you want to continue? (y/N): ").lower().strip()
            
            if confirm != 'y':
                print("Operation cancelled.")
                return
            
            # Clear all data
            db.session.query(User).delete()
            db.session.query(Document).delete()
            db.session.query(Room).delete()
            
            # Commit the changes
            db.session.commit()
            
            print(f"Cleared: {user_count} users, {document_count} documents, {room_count} rooms")
            print("Database data cleared successfully!")
            print("\nThe server can continue running - refresh your frontend to see the clean state.")
            
        except Exception as e:
            print(f"Error clearing database data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    clear_database_data()