import os
import json
import apsw
import numpy as np
import traceback
from nicegui import ui, run

# This function handles the DB connection locally to avoid threading issues.
def load_and_prepare_vectors(db_file, sql_table):
    entries = []
    entry_vectors = []
    
    with apsw.Connection(db_file) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT path, entry, entry_vector FROM {sql_table}")
        
        # This loop is CPU intensive because of json.loads and tuple unpacking
        for path, entry, vector_json in cursor.fetchall():
            if path and entry and vector_json:
                # Format the entry label immediately
                entries.append(f"[{path}] {entry}")
                # Parse the vector (Heavy CPU operation)
                entry_vectors.append(np.array(json.loads(vector_json)))

    if not entries:
        return [], None

    # Stacking arrays is also CPU intensive
    document_matrix = np.vstack(entry_vectors)
    return entries, document_matrix


async def fetch_bible_dictionaries_matches_async(query):
    n = ui.notification("Loading ...", timeout=None, spinner=True)
    db_file = os.path.join(BIBLEMATEGUI_DATA, "vectors", "dictionary.db")
    sql_table = "Dictionary"
    embedding_model = "paraphrase-multilingual"
    path = ""
    options = []

    try:
        # We need a quick connection just to check for EXACT matches first
        # (This is usually fast enough to keep on the main thread, but can be offloaded too if needed)
        exact_match_found = False
        with apsw.Connection(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {sql_table} WHERE entry = ?;", (query,))
            rows = cursor.fetchall()
            
            if len(rows) == 1:
                path = rows[0][0]
                exact_match_found = True
            elif len(rows) > 1:
                options = [f"[{row[0]}] {row[1]}" for row in rows]
                exact_match_found = True

        # If no exact match, proceed to Similarity Search
        if not exact_match_found:
            # 1. Get Query Vector (Already doing this correctly)
            query_vector = await run.io_bound(get_embeddings, [query], embedding_model)
            query_vector = query_vector[0]

            # 2. HEAVY LIFTING: Run the new helper function in a separate process
            # This prevents the "Connection Lost" error
            entries, document_matrix = await run.cpu_bound(load_and_prepare_vectors, db_file, sql_table)

            if not entries:
                return []

            # 3. Compute Similarity (Already doing this correctly)
            similarities = await run.cpu_bound(cosine_similarity_matrix, query_vector, document_matrix)
            
            # 4. Sort and select top results
            top_indices = np.argsort(similarities)[::-1][:app.storage.user["top_similar_entries"]]
            options = [entries[i] for i in top_indices]

    except Exception as ex:
        print("Error during database operation:", ex)
        traceback.print_exc()
        n.message = f'Error: {str(ex)}'
        n.type = 'negative'
        return
    finally:
        n.dismiss()
        
    return path, options