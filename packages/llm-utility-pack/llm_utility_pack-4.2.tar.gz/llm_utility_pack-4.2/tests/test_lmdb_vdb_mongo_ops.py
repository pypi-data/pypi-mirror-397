import unittest
import shutil
import tempfile
import os
import numpy as np
import faiss
import logging
import operator
import decimal
from collections import defaultdict
from datetime import datetime

# Ensure lightning_disk_kv is installed
try:
    from lightning_disk_kv import LDKV
except ImportError:
    raise ImportError("The 'lightning_disk_kv' library is required. Please install it.")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# ==========================================
# Updated LmdbVectorDB Implementation
# ==========================================

class LmdbVectorDB:
    """
    A persistent, low-RAM vector database that filters first, then loads vectors.
    Supports complex MongoDB-style queries ($and, $or, $gt, $in, etc).
    """

    OP_MAP = {
        "$gt": operator.gt,
        "$gte": operator.ge,
        "$lt": operator.lt,
        "$lte": operator.le,
        "$ne": operator.ne
    }

    def __init__(self, storage_base_path="vectordb_data", num_shards=8):
        # Initialize 3 separate KV stores for logical separation
        self.vector_storage = LDKV(os.path.join(storage_base_path, "vectors"), num_shards=num_shards)
        self.metadata_storage = LDKV(os.path.join(storage_base_path, "metadata"), num_shards=num_shards)
        self.metadata_index_storage = LDKV(os.path.join(storage_base_path, "metadata_index"), num_shards=num_shards)
        
        os.makedirs(storage_base_path, exist_ok=True)

    def _format_for_indexing(self, value):
        """Formats values for lexicographical sorting in LMDB (B-Tree)."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, (int, float)):
            # Normalize numbers to fixed length strings for string comparison
            # Offset to handle negatives: 2**63. 
            offset = decimal.Decimal(2**63)
            return f"{decimal.Decimal(value) + offset:064.8f}"
        return str(value)

    def _normalize(self, vector):
        """Normalize vector to unit length for Cosine Similarity."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def store_embedding(self, unique_id, embedding, metadata_dict={}):
        self.store_embeddings_batch([unique_id], [embedding], [metadata_dict])

    def store_embeddings_batch(self, unique_ids, embeddings, metadata_dicts=None):
        if metadata_dicts is None:
            metadata_dicts = [{} for _ in unique_ids]

        # 1. Prepare Vectors (Normalize -> Bytes)
        vector_bytes_list = []
        for vec in embeddings:
            vec_np = np.array(vec, dtype=np.float32)
            vec_norm = self._normalize(vec_np)
            vector_bytes_list.append(vec_norm.tobytes())

        # 2. Store Raw Data
        self.vector_storage.store_data(vector_bytes_list, unique_ids)
        self.metadata_storage.store_data(metadata_dicts, unique_ids)

        # 3. Update Metadata Index (Inverted Index)
        updates = defaultdict(set)
        for uid, meta in zip(unique_ids, metadata_dicts):
            for key, value in meta.items():
                formatted_value = self._format_for_indexing(value)
                index_key = f"idx_{key}:{formatted_value}"
                updates[index_key].add(uid)
        
        if updates:
            def merge_ids(existing, new_ids):
                if existing is None: return new_ids
                return existing | new_ids
            self.metadata_index_storage.batch_atomic_update(updates, merge_ids)

    def delete(self, metadata_query):
        """
        Deletes documents matching the metadata query.
        """
        ids_to_delete_set = self._get_filtered_ids(metadata_query)
        if not ids_to_delete_set:
            return 0
        
        ids_to_delete = list(ids_to_delete_set)
        
        # Cleanup Metadata Index
        metadatas = self.metadata_storage.get_data(ids_to_delete)
        meta_index_removals = defaultdict(set)
        
        for doc_id, meta in zip(ids_to_delete, metadatas):
            if meta:
                for key, value in meta.items():
                    formatted_value = self._format_for_indexing(value)
                    index_key = f"idx_{key}:{formatted_value}"
                    meta_index_removals[index_key].add(doc_id)

        def remove_ids(existing, ids_to_remove):
            if existing is None: return None
            return existing - ids_to_remove

        if meta_index_removals:
            self.metadata_index_storage.batch_atomic_update(meta_index_removals, remove_ids)

        # Delete Raw Data
        self.vector_storage.delete_data(ids_to_delete)
        self.metadata_storage.delete_data(ids_to_delete)
        
        return len(ids_to_delete)

    def _resolve_leaf_condition(self, key, value_or_op):
        """
        Resolves a single key-value condition to a set of IDs.
        """
        found_ids = set()

        if isinstance(value_or_op, dict):
            first_op = True
            for op_str, op_val in value_or_op.items():
                current_op_ids = set()
                
                if op_str == "$in":
                    for v in op_val:
                        formatted_v = self._format_for_indexing(v)
                        index_key = f"idx_{key}:{formatted_v}"
                        ids_data = self.metadata_index_storage.get_data([index_key])
                        if ids_data and ids_data[0]:
                            current_op_ids.update(ids_data[0])
                else:
                    # Range Queries
                    start_key, end_key = "", ""
                    prefix = f"idx_{key}:"
                    val_formatted = self._format_for_indexing(op_val)

                    if op_str == "$gte":
                        start_key = prefix + val_formatted
                        end_key = prefix + "~" 
                    elif op_str == "$gt":
                        start_key = prefix + val_formatted + "\0"
                        end_key = prefix + "~"
                    elif op_str == "$lte":
                        start_key = prefix
                        end_key = prefix + val_formatted + "\0"
                    elif op_str == "$lt":
                        start_key = prefix
                        end_key = prefix + val_formatted
                    elif op_str == "$ne":
                         # Get all IDs for this key, subtract exact match
                         all_key_ids = set()
                         for _, ids in self.metadata_index_storage.items_in_range(prefix, prefix + "~", prefix):
                             if ids: all_key_ids.update(ids)
                         
                         exact_key = f"idx_{key}:{val_formatted}"
                         exact_ids_data = self.metadata_index_storage.get_data([exact_key])
                         if exact_ids_data and exact_ids_data[0]:
                             current_op_ids = all_key_ids - exact_ids_data[0]
                         else:
                             current_op_ids = all_key_ids
                    
                    if op_str != "$ne":
                        for _, ids in self.metadata_index_storage.items_in_range(start_key, end_key, prefix):
                            if ids:
                                current_op_ids.update(ids)
                
                if first_op:
                    found_ids = current_op_ids
                    first_op = False
                else:
                    found_ids &= current_op_ids
        else:
            # Exact Match
            index_key = f"idx_{key}:{self._format_for_indexing(value_or_op)}"
            ids_data = self.metadata_index_storage.get_data([index_key])
            if ids_data and ids_data[0]:
                found_ids = ids_data[0]
        
        return found_ids

    def _evaluate_query(self, query):
        """
        Recursively evaluates a query dictionary.
        """
        if not query:
            return None

        candidates = None 
        
        for k, v in query.items():
            current_ids = set()
            
            if k == "$or":
                for sub_q in v:
                    sub_res = self._evaluate_query(sub_q)
                    if sub_res is None:
                        # Union with Universe = Universe
                        current_ids = None 
                        break
                    current_ids.update(sub_res)
            
            elif k == "$and":
                first_and = True
                for sub_q in v:
                    sub_res = self._evaluate_query(sub_q)
                    if first_and:
                        current_ids = sub_res
                        first_and = False
                    else:
                        if current_ids is None:
                            current_ids = sub_res
                        elif sub_res is not None:
                            current_ids &= sub_res
            
            else:
                current_ids = self._resolve_leaf_condition(k, v)

            if candidates is None:
                candidates = current_ids
            else:
                if current_ids is None:
                    pass
                elif candidates is None: 
                    candidates = current_ids
                else:
                    candidates &= current_ids
            
            if candidates is not None and len(candidates) == 0:
                return set()

        return candidates

    def _get_filtered_ids(self, metadata_query):
        if not metadata_query:
            return set(self.vector_storage.keys())

        result_ids = self._evaluate_query(metadata_query)
        
        if result_ids is None:
            return set(self.vector_storage.keys())
            
        return result_ids

    def _get_vector_dimension(self, sample_id):
        raw = self.vector_storage.get_data([sample_id])
        if raw and raw[0]:
            vec = np.frombuffer(raw[0], dtype=np.float32)
            return vec.shape[0]
        return 0

    def search(self, query_embedding, metadata_filter=None, k=5, max_ram_usage_gb=None):
        candidate_ids = self._get_filtered_ids(metadata_filter)
        if not candidate_ids:
            return []
        
        candidate_ids_list = list(candidate_ids)
        total_candidates = len(candidate_ids_list)
        batch_size = total_candidates
        
        if max_ram_usage_gb is not None:
            dim = self._get_vector_dimension(candidate_ids_list[0])
            if dim == 0: return []
            bytes_per_vec = dim * 4
            max_bytes = max_ram_usage_gb * (1024 ** 3)
            safe_count = int(max_bytes / (bytes_per_vec * 2.5))
            batch_size = max(1000, safe_count)

        q_np = np.array([query_embedding], dtype=np.float32)
        q_norm = self._normalize(q_np)
        
        global_top_candidates = [] 
        
        for i in range(0, total_candidates, batch_size):
            batch_ids = candidate_ids_list[i : i + batch_size]
            raw_vectors = self.vector_storage.get_data(batch_ids)
            
            valid_candidates = []
            valid_vectors = []
            
            for uid, vec_bytes in zip(batch_ids, raw_vectors):
                if vec_bytes is not None:
                    valid_candidates.append(uid)
                    valid_vectors.append(np.frombuffer(vec_bytes, dtype=np.float32))

            if not valid_vectors: continue

            batch_matrix = np.stack(valid_vectors)
            dim = batch_matrix.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(batch_matrix)

            k_search = min(k, len(valid_candidates))
            distances, indices = index.search(q_norm, k_search)
            
            for j, matrix_idx in enumerate(indices[0]):
                if matrix_idx != -1:
                    score = float(distances[0][j])
                    uid = valid_candidates[matrix_idx]
                    global_top_candidates.append((score, uid))
            
            global_top_candidates.sort(key=lambda x: x[0], reverse=True)
            global_top_candidates = global_top_candidates[:k]

        final_ids = [uid for _, uid in global_top_candidates]
        final_scores = [score for score, _ in global_top_candidates]
        
        if not final_ids: return []

        final_metas = self.metadata_storage.get_data(final_ids)
        
        results = []
        for i, uid in enumerate(final_ids):
            results.append((uid, final_scores[i], final_metas[i]))
            
        return results

# ==========================================
# Unit Tests
# ==========================================

class TestLmdbVectorDB(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for DB storage
        self.test_dir = tempfile.mkdtemp()
        self.db = LmdbVectorDB(storage_base_path=self.test_dir, num_shards=2)

        # Dummy Data
        # A: [1.0, 0.0] -> Normalized: [1.0, 0.0]
        # B: [0.9, 0.1] -> Normalized approx [0.993, 0.110]
        # C: [0.0, 1.0]
        # D: [0.5, 0.5]
        # E: [0.1, 0.9]
        
        self.vectors = [
            [1.0, 0.0], 
            [0.9, 0.1], 
            [0.0, 1.0], 
            [0.5, 0.5], 
            [0.1, 0.9]
        ]
        self.ids = ["doc_A", "doc_B", "doc_C", "doc_D", "doc_E"]
        self.metas = [
            {"category": "news", "views": 100, "author": "Alice"},
            {"category": "news", "views": 200, "author": "Bob"},
            {"category": "sports", "views": 50, "author": "Alice"},
            {"category": "sports", "views": 150, "author": "Charlie"},
            {"category": "tech", "views": 300, "author": "Bob"}
        ]
        
        self.db.store_embeddings_batch(self.ids, self.vectors, self.metas)

    def tearDown(self):
        # Clean up the temporary directory
        self.db.vector_storage.close()
        self.db.metadata_storage.close()
        self.db.metadata_index_storage.close()
        shutil.rmtree(self.test_dir)

    def test_exact_match(self):
        # Query: category == "news"
        res = self.db._get_filtered_ids({"category": "news"})
        self.assertEqual(res, {"doc_A", "doc_B"})

    def test_implicit_and(self):
        # Query: category == "news" AND author == "Bob"
        res = self.db._get_filtered_ids({"category": "news", "author": "Bob"})
        self.assertEqual(res, {"doc_B"})

    def test_numeric_range_gt(self):
        # Query: views > 100 -> 150 (D), 200 (B), 300 (E)
        res = self.db._get_filtered_ids({"views": {"$gt": 100}})
        self.assertEqual(res, {"doc_B", "doc_D", "doc_E"})

    def test_numeric_range_lte(self):
        # Query: views <= 100 -> 100 (A), 50 (C)
        res = self.db._get_filtered_ids({"views": {"$lte": 100}})
        self.assertEqual(res, {"doc_A", "doc_C"})

    def test_in_operator(self):
        # Query: author IN ["Alice", "Charlie"] -> A, C, D
        res = self.db._get_filtered_ids({"author": {"$in": ["Alice", "Charlie"]}})
        self.assertEqual(res, {"doc_A", "doc_C", "doc_D"})

    def test_operator_or(self):
        # Query: category == "tech" (E) OR views < 60 (C)
        query = {
            "$or": [
                {"category": "tech"},
                {"views": {"$lt": 60}}
            ]
        }
        res = self.db._get_filtered_ids(query)
        self.assertEqual(res, {"doc_E", "doc_C"})

    def test_operator_and_explicit(self):
        # Query: (views > 100) AND (author == "Bob") -> B (200), E (300)
        query = {
            "$and": [
                {"views": {"$gt": 100}},
                {"author": "Bob"}
            ]
        }
        res = self.db._get_filtered_ids(query)
        self.assertEqual(res, {"doc_B", "doc_E"})

    def test_nested_logic(self):
        # Query: (category == "news") AND ( (views < 150) OR (author == "Bob") )
        # News: A, B.
        # Condition 2:
        #   views < 150 -> A, C
        #   author == Bob -> B, E
        #   Union -> A, B, C, E
        # Intersection -> A, B
        query = {
            "category": "news",
            "$or": [
                {"views": {"$lt": 150}},
                {"author": "Bob"}
            ]
        }
        res = self.db._get_filtered_ids(query)
        self.assertEqual(res, {"doc_A", "doc_B"})

    def test_nested_complex_or(self):
        # Query: OR( AND(sports, >100 views), AND(news, <150 views) )
        # 1. Sports & >100 -> D
        # 2. News & <150 -> A
        # Result -> D, A
        query = {
            "$or": [
                {"$and": [
                    {"category": "sports"},
                    {"views": {"$gt": 100}}
                ]},
                {"$and": [
                    {"category": "news"},
                    {"views": {"$lt": 150}}
                ]}
            ]
        }
        res = self.db._get_filtered_ids(query)
        self.assertEqual(res, {"doc_D", "doc_A"})

    def test_empty_query(self):
        # Empty query should return all IDs
        res = self.db._get_filtered_ids({})
        self.assertEqual(len(res), 5)

    def test_ne_operator(self):
        # Query: author != "Alice"
        # Alice is in A and C.
        # Expect B, D, E.
        res = self.db._get_filtered_ids({"author": {"$ne": "Alice"}})
        self.assertEqual(res, {"doc_B", "doc_D", "doc_E"})

    def test_search_integration(self):
        # Search for vector close to doc_A [1, 0]
        # Restrict to 'news' (A, B)
        # A should be top result.
        
        q_vec = [1.0, 0.0]
        results = self.db.search(q_vec, metadata_filter={"category": "news"}, k=2)
        
        self.assertEqual(len(results), 2)
        
        # Check first result is A
        uid_0, score_0, meta_0 = results[0]
        self.assertEqual(uid_0, "doc_A")
        self.assertAlmostEqual(score_0, 1.0, places=4)
        
        # Check second result is B
        uid_1, score_1, meta_1 = results[1]
        self.assertEqual(uid_1, "doc_B")

    def test_delete_logic(self):
        # Delete all documents where views < 100 (C, sports, 50)
        # doc_C should be gone.
        
        count = self.db.delete({"views": {"$lt": 100}})
        self.assertEqual(count, 1) # Only C has 50 views
        
        # Verify C is gone
        res = self.db._get_filtered_ids({"category": "sports"})
        self.assertEqual(res, {"doc_D"}) # C was sports, now deleted
        
        # Verify metadata index for C is cleaned (views=50 should point to nothing)
        # We can check by querying specifically for views=50
        res_empty = self.db._get_filtered_ids({"views": 50})
        self.assertEqual(res_empty, set())

if __name__ == "__main__":
    unittest.main()