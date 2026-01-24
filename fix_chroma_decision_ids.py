#!/usr/bin/env python3
# Script to fix decision_id metadata in Chroma database
# The existing records have decision_id=0 instead of the actual IDs

import sqlite3
import os

CHROMA_DB_PATH = "chroma_memory/chroma.sqlite3"
MEMORY_DB_PATH = "long_term_memory.db"

print("="*60)
print("CHROMA DECISION_ID FIX SCRIPT")
print("="*60)

# Check if databases exist
if not os.path.exists(CHROMA_DB_PATH):
    print(f"❌ Chroma database not found: {CHROMA_DB_PATH}")
    exit(1)

if not os.path.exists(MEMORY_DB_PATH):
    print(f"❌ Memory database not found: {MEMORY_DB_PATH}")
    exit(1)

# Connect to both databases
chroma_conn = sqlite3.connect(CHROMA_DB_PATH)
memory_conn = sqlite3.connect(MEMORY_DB_PATH)

# Get all questions from memory DB with their IDs
print("\n📊 Loading decisions from memory database...")
memory_cursor = memory_conn.cursor()
memory_cursor.execute("SELECT id, question FROM decisions ORDER BY id")
decisions = memory_cursor.fetchall()
print(f"✅ Found {len(decisions)} decisions in memory database")

# Get all embeddings with their document text
print("\n📊 Loading embeddings from Chroma...")
chroma_cursor = chroma_conn.cursor()

# Get embeddings with their documents
chroma_cursor.execute("""
    SELECT e.id, em.string_value as document
    FROM embeddings e
    JOIN embedding_metadata em ON e.id = em.id
    WHERE em.key = 'chroma:document'
    ORDER BY e.id
""")
embeddings = chroma_cursor.fetchall()
print(f"✅ Found {len(embeddings)} embeddings in Chroma")

# Create mapping: question -> decision_id
question_to_id = {question: dec_id for dec_id, question in decisions}

# Update decision_id metadata for each embedding
print("\n🔧 Fixing decision_id metadata...")
fixed_count = 0
not_found_count = 0

for embedding_id, document in embeddings:
    if document in question_to_id:
        correct_decision_id = question_to_id[document]
        
        # Update the decision_id metadata
        chroma_cursor.execute("""
            UPDATE embedding_metadata
            SET int_value = ?
            WHERE id = ? AND key = 'decision_id'
        """, (correct_decision_id, embedding_id))
        
        fixed_count += 1
        if fixed_count <= 5:  # Show first 5
            print(f"   ✅ Fixed embedding {embedding_id}: decision_id={correct_decision_id}")
    else:
        not_found_count += 1
        if not_found_count <= 3:  # Show first 3
            print(f"   ⚠️  No match for embedding {embedding_id}: '{document[:50]}...'")

# Commit changes
chroma_conn.commit()
print(f"\n✅ Fixed {fixed_count} embeddings")
if not_found_count > 0:
    print(f"⚠️  Could not match {not_found_count} embeddings")

# Verify fix
print("\n🔍 Verifying fix...")
chroma_cursor.execute("""
    SELECT DISTINCT int_value
    FROM embedding_metadata
    WHERE key = 'decision_id'
    ORDER BY int_value
    LIMIT 10
""")
unique_ids = chroma_cursor.fetchall()
print(f"✅ Sample of unique decision_ids after fix: {[row[0] for row in unique_ids]}")

# Close connections
chroma_conn.close()
memory_conn.close()

print("\n" + "="*60)
print("FIX COMPLETE!")
print("="*60)
print("\nYou can now restart the application and test the Historical Decisions tab.")
