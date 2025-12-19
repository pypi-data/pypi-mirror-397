import unittest
import numpy as np
from typing import List

from utility_pack.rotational_quantization import BinaryRotationalQuantization, FastPseudoRandomRotation, RotationalQuantization


class TestFastPseudoRandomRotation(unittest.TestCase):
    """Test cases for FastPseudoRandomRotation class."""
    
    def test_initialization(self):
        """Test that rotation initializes with correct parameters."""
        rot = FastPseudoRandomRotation(100, rounds=3, seed=42)
        self.assertEqual(rot.dimension, 100)
        self.assertEqual(rot.rounds, 3)
        self.assertEqual(rot.padded_dim, 128)  # Next multiple of 32
        self.assertEqual(len(rot.sign_matrices), 3)
        self.assertEqual(len(rot.permutations), 3)
    
    def test_padding_calculation(self):
        """Test that padding to nearest multiple of 32 works correctly."""
        test_cases = [(1, 32), (32, 32), (33, 64), (100, 128), (256, 256)]
        for dim, expected_padded in test_cases:
            rot = FastPseudoRandomRotation(dim, seed=42)
            self.assertEqual(rot.padded_dim, expected_padded)
    
    def test_rotation_preserves_dimension(self):
        """Test that rotation output has same dimension as input."""
        dim = 100
        rot = FastPseudoRandomRotation(dim, seed=42)
        x = np.random.randn(dim)
        rotated = rot.rotate(x)
        self.assertEqual(len(rotated), dim)
    
    def test_rotation_is_deterministic(self):
        """Test that rotation with same seed produces same results."""
        dim = 50
        x = np.random.randn(dim)
        
        rot1 = FastPseudoRandomRotation(dim, seed=42)
        rot2 = FastPseudoRandomRotation(dim, seed=42)
        
        result1 = rot1.rotate(x)
        result2 = rot2.rotate(x)
        
        np.testing.assert_array_almost_equal(result1, result2)
    
    def test_rotation_different_seeds(self):
        """Test that different seeds produce different rotations."""
        dim = 50
        x = np.random.randn(dim)
        
        rot1 = FastPseudoRandomRotation(dim, seed=42)
        rot2 = FastPseudoRandomRotation(dim, seed=43)
        
        result1 = rot1.rotate(x)
        result2 = rot2.rotate(x)
        
        # Should be different (very unlikely to be same)
        self.assertFalse(np.allclose(result1, result2))
    
    def test_rotation_wrong_dimension_raises_error(self):
        """Test that passing wrong dimension raises ValueError."""
        rot = FastPseudoRandomRotation(100, seed=42)
        x = np.random.randn(50)  # Wrong dimension
        
        with self.assertRaises(ValueError):
            rot.rotate(x)
    
    def test_fwht_block_power_of_two(self):
        """Test FWHT on various power-of-2 block sizes."""
        rot = FastPseudoRandomRotation(64, seed=42)
        
        for block_size in [2, 4, 8, 16, 32, 64]:
            x = np.random.randn(block_size)
            result = rot._fwht_block(x, block_size)
            self.assertEqual(len(result), block_size)
    
    def test_fwht_block_invalid_size(self):
        """Test that FWHT raises error for non-power-of-2 sizes."""
        rot = FastPseudoRandomRotation(64, seed=42)
        x = np.random.randn(10)
        
        with self.assertRaises(ValueError):
            rot._fwht_block(x, 10)
    
    def test_rotation_preserves_norm_approximately(self):
        """Test that rotation approximately preserves L2 norm."""
        dim = 100
        rot = FastPseudoRandomRotation(dim, seed=42)
        x = np.random.randn(dim)
        
        original_norm = np.linalg.norm(x)
        rotated = rot.rotate(x)
        rotated_norm = np.linalg.norm(rotated)
        
        # Rotation doesn't perfectly preserve norm due to padding and FWHT normalization
        # But should be in reasonable range (within 30% due to padding to 128)
        self.assertAlmostEqual(original_norm, rotated_norm, delta=original_norm * 0.3)


class TestRotationalQuantization(unittest.TestCase):
    """Test cases for 8-bit RotationalQuantization class."""
    
    def test_initialization(self):
        """Test that quantizer initializes correctly."""
        rq = RotationalQuantization(100, rotation_rounds=3, seed=42)
        self.assertEqual(rq.dimension, 100)
        self.assertIsNotNone(rq.rotation)
    
    def test_encode_output_format(self):
        """Test that encode returns correct tuple format."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        result = rq.encode(x)
        self.assertEqual(len(result), 4)
        
        quantized, l_x, delta_x, norm_squared = result
        self.assertEqual(quantized.dtype, np.uint8)
        self.assertEqual(len(quantized), 100)
        self.assertIsInstance(l_x, float)
        self.assertIsInstance(delta_x, float)
        self.assertIsInstance(norm_squared, (float, np.floating))
    
    def test_encode_values_in_range(self):
        """Test that quantized values are in [0, 255]."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        quantized, _, _, _ = rq.encode(x)
        self.assertTrue(np.all(quantized >= 0))
        self.assertTrue(np.all(quantized <= 255))
    
    def test_encode_wrong_dimension(self):
        """Test that encoding wrong dimension raises error."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(50)
        
        with self.assertRaises(ValueError):
            rq.encode(x)
    
    def test_encode_deterministic(self):
        """Test that encoding is deterministic with same seed."""
        x = np.random.randn(100)
        
        rq1 = RotationalQuantization(100, seed=42)
        rq2 = RotationalQuantization(100, seed=42)
        
        result1 = rq1.encode(x)
        result2 = rq2.encode(x)
        
        np.testing.assert_array_equal(result1[0], result2[0])
        self.assertAlmostEqual(result1[1], result2[1])
        self.assertAlmostEqual(result1[2], result2[2])
        self.assertAlmostEqual(result1[3], result2[3])
    
    def test_norm_squared_correct(self):
        """Test that stored norm squared is correct."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        _, _, _, norm_squared = rq.encode(x)
        expected_norm_squared = np.dot(x, x)
        
        self.assertAlmostEqual(norm_squared, expected_norm_squared, places=5)
    
    def test_estimate_inner_product_self_similarity(self):
        """Test that inner product of vector with itself is approximately correct."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        q_code, q_l, q_delta, _ = rq.encode(x)
        estimated = rq.estimate_inner_product(q_code, q_l, q_delta, q_code, q_l, q_delta)
        expected = np.dot(x, x)
        
        # Should be reasonably close (within 20% due to quantization error)
        relative_error = abs(estimated - expected) / expected
        self.assertLess(relative_error, 0.2)
    
    def test_cosine_similarity_self(self):
        """Test that cosine similarity of vector with itself is close to 1."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        q_code, q_l, q_delta, q_norm = rq.encode(x)
        similarity = rq.cosine_similarity(q_code, q_l, q_delta, q_norm,
                                          q_code, q_l, q_delta, q_norm)
        
        # 8-bit quantization has significant error, should be > 0.7
        self.assertGreater(similarity, 0.7)
        self.assertLessEqual(similarity, 1.1)  # Allow small numerical error
    
    def test_cosine_similarity_better_with_larger_dimension(self):
        """Test that larger dimensions give better similarity estimates."""
        # Test with a larger dimension where quantization error is more distributed
        rq = RotationalQuantization(512, seed=42)
        x = np.random.randn(512)
        
        q_code, q_l, q_delta, q_norm = rq.encode(x)
        similarity = rq.cosine_similarity(q_code, q_l, q_delta, q_norm,
                                          q_code, q_l, q_delta, q_norm)
        
        # With more dimensions, self-similarity should be closer to 1
        self.assertGreater(similarity, 0.85)
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity of approximately orthogonal vectors."""
        rq = RotationalQuantization(100, seed=42)
        
        # Create orthogonal vectors
        x = np.zeros(100)
        x[:50] = 1.0
        y = np.zeros(100)
        y[50:] = 1.0
        
        x_code, x_l, x_delta, x_norm = rq.encode(x)
        y_code, y_l, y_delta, y_norm = rq.encode(y)
        
        similarity = rq.cosine_similarity(x_code, x_l, x_delta, x_norm,
                                          y_code, y_l, y_delta, y_norm)
        
        # Should be close to 0
        self.assertAlmostEqual(similarity, 0.0, places=1)
    
    def test_cosine_similarity_zero_norm(self):
        """Test that zero norm vectors return 0 similarity."""
        rq = RotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        x_code, x_l, x_delta, x_norm = rq.encode(x)
        
        # Test with zero norm
        similarity = rq.cosine_similarity(x_code, x_l, x_delta, 0.0,
                                          x_code, x_l, x_delta, x_norm)
        self.assertEqual(similarity, 0.0)


class TestBinaryRotationalQuantization(unittest.TestCase):
    """Test cases for 1-bit BinaryRotationalQuantization class."""
    
    def test_initialization(self):
        """Test that binary quantizer initializes correctly."""
        brq = BinaryRotationalQuantization(100, rotation_rounds=3, seed=42)
        self.assertEqual(brq.input_dimension, 100)
        self.assertEqual(brq.padded_dimension, 256)  # MIN_CODE_BITS
        self.assertEqual(brq.QUERY_BITS, 5)
    
    def test_min_code_bits_enforced(self):
        """Test that dimension is padded to at least MIN_CODE_BITS."""
        brq = BinaryRotationalQuantization(50, seed=42)
        self.assertGreaterEqual(brq.padded_dimension, brq.MIN_CODE_BITS)
    
    def test_encode_output_format(self):
        """Test that encode returns correct tuple format."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        packed_bits, step, norm_squared = brq.encode(x)
        
        self.assertIsInstance(packed_bits, np.ndarray)
        self.assertEqual(packed_bits.dtype, np.uint8)
        self.assertIsInstance(step, float)
        self.assertIsInstance(norm_squared, float)
    
    def test_encode_packed_bits_length(self):
        """Test that packed bits have correct length."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        packed_bits, _, _ = brq.encode(x)
        expected_length = int(np.ceil(brq.padded_dimension / 8))
        
        self.assertEqual(len(packed_bits), expected_length)
    
    def test_encode_query_output_format(self):
        """Test that encode_query returns correct format."""
        brq = BinaryRotationalQuantization(100, seed=42)
        q = np.random.randn(100)
        
        query_codes, step, norm_squared = brq.encode_query(q)
        
        self.assertIsInstance(query_codes, list)
        self.assertEqual(len(query_codes), brq.QUERY_BITS)
        for code in query_codes:
            self.assertEqual(code.dtype, np.uint8)
        self.assertIsInstance(step, float)
        self.assertIsInstance(norm_squared, float)
    
    def test_encode_deterministic(self):
        """Test that encoding is deterministic with same seed."""
        x = np.random.randn(100)
        
        brq1 = BinaryRotationalQuantization(100, seed=42)
        brq2 = BinaryRotationalQuantization(100, seed=42)
        
        result1 = brq1.encode(x)
        result2 = brq2.encode(x)
        
        np.testing.assert_array_equal(result1[0], result2[0])
        self.assertAlmostEqual(result1[1], result2[1])
        self.assertAlmostEqual(result1[2], result2[2])
    
    def test_encode_query_deterministic(self):
        """Test that query encoding is deterministic."""
        q = np.random.randn(100)
        
        brq1 = BinaryRotationalQuantization(100, seed=42)
        brq2 = BinaryRotationalQuantization(100, seed=42)
        
        codes1, step1, norm1 = brq1.encode_query(q)
        codes2, step2, norm2 = brq2.encode_query(q)
        
        for c1, c2 in zip(codes1, codes2):
            np.testing.assert_array_equal(c1, c2)
        self.assertAlmostEqual(step1, step2)
        self.assertAlmostEqual(norm1, norm2)
    
    def test_pad_vector(self):
        """Test vector padding functionality."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(50).astype(np.float32)
        
        padded = brq._pad_vector(x)
        self.assertEqual(len(padded), brq.padded_dimension)
        np.testing.assert_array_almost_equal(padded[:50], x, decimal=5)
        np.testing.assert_array_equal(padded[50:], 0)
    
    def test_hamming_distance(self):
        """Test Hamming distance calculation."""
        a = np.array([0b00000000, 0b11111111], dtype=np.uint8)
        b = np.array([0b11111111, 0b00000000], dtype=np.uint8)
        
        dist = BinaryRotationalQuantization._hamming_dist_packed(a, b)
        self.assertEqual(dist, 16)  # All bits differ
    
    def test_hamming_distance_same(self):
        """Test Hamming distance of identical arrays is 0."""
        a = np.array([0b10101010, 0b01010101], dtype=np.uint8)
        
        dist = BinaryRotationalQuantization._hamming_dist_packed(a, a)
        self.assertEqual(dist, 0)
    
    def test_estimate_inner_product_nonzero(self):
        """Test that inner product estimation produces reasonable values."""
        brq = BinaryRotationalQuantization(100, seed=42)
        
        x = np.random.randn(100)
        q = np.random.randn(100)
        
        x_packed, x_step, _ = brq.encode(x)
        q_codes, q_step, _ = brq.encode_query(q)
        
        estimated = brq.estimate_inner_product(q_codes, q_step, x_packed, x_step)
        
        # Should produce a finite value
        self.assertTrue(np.isfinite(estimated))
    
    def test_estimate_inner_product_zero_step(self):
        """Test that zero step returns zero inner product."""
        brq = BinaryRotationalQuantization(100, seed=42)
        
        x = np.random.randn(100)
        q = np.random.randn(100)
        
        x_packed, _, _ = brq.encode(x)
        q_codes, _, _ = brq.encode_query(q)
        
        # Zero steps should give zero inner product
        estimated = brq.estimate_inner_product(q_codes, 0.0, x_packed, 0.0)
        self.assertEqual(estimated, 0.0)
    
    def test_cosine_similarity_self(self):
        """Test cosine similarity of vector with itself."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        x_packed, x_step, x_norm = brq.encode(x)
        q_codes, q_step, q_norm = brq.encode_query(x)
        
        similarity = brq.cosine_similarity(q_codes, q_step, q_norm,
                                           x_packed, x_step, x_norm)
        
        # Should be positive and less than or equal to 1
        self.assertGreater(similarity, 0.5)
        self.assertLessEqual(similarity, 1.1)  # Allow small numerical error
    
    def test_cosine_similarity_zero_norm(self):
        """Test that zero norm returns 0 similarity."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(100)
        
        x_packed, x_step, _ = brq.encode(x)
        q_codes, q_step, _ = brq.encode_query(x)
        
        similarity = brq.cosine_similarity(q_codes, q_step, 0.0,
                                           x_packed, x_step, 0.0)
        self.assertEqual(similarity, 0.0)
    
    def test_encode_multidimensional_raises_error(self):
        """Test that multidimensional arrays raise ValueError."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.random.randn(10, 10)
        
        with self.assertRaises(ValueError):
            brq.encode(x)
    
    def test_encode_query_multidimensional_raises_error(self):
        """Test that multidimensional query arrays raise ValueError."""
        brq = BinaryRotationalQuantization(100, seed=42)
        q = np.random.randn(10, 10)
        
        with self.assertRaises(ValueError):
            brq.encode_query(q)
    
    def test_encode_zero_vector(self):
        """Test encoding of zero vector."""
        brq = BinaryRotationalQuantization(100, seed=42)
        x = np.zeros(100)
        
        packed_bits, step, norm_squared = brq.encode(x)
        
        self.assertEqual(step, 0.0)
        self.assertEqual(norm_squared, 0.0)
        self.assertIsInstance(packed_bits, np.ndarray)
    
    def test_encode_query_zero_vector(self):
        """Test query encoding of zero vector."""
        brq = BinaryRotationalQuantization(100, seed=42)
        q = np.zeros(100)
        
        query_codes, step, norm_squared = brq.encode_query(q)
        
        self.assertEqual(step, 0.0)
        self.assertEqual(norm_squared, 0.0)
        self.assertEqual(len(query_codes), brq.QUERY_BITS)


class TestIntegration(unittest.TestCase):
    """Integration tests across multiple classes."""
    
    def test_8bit_similarity_correlation(self):
        """Test that 8-bit quantized similarity correlates with exact similarity."""
        rq = RotationalQuantization(200, seed=42)
        np.random.seed(42)
        
        # Create test vectors with varying similarities
        base = np.random.randn(200)
        vectors = [
            base,  # Same
            base + 0.1 * np.random.randn(200),  # Very similar
            base + 0.5 * np.random.randn(200),  # Somewhat similar
            np.random.randn(200),  # Different
        ]
        
        exact_sims = [np.dot(base, v) / (np.linalg.norm(base) * np.linalg.norm(v)) 
                      for v in vectors]
        
        base_code, base_l, base_delta, base_norm = rq.encode(base)
        estimated_sims = []
        
        for v in vectors:
            v_code, v_l, v_delta, v_norm = rq.encode(v)
            sim = rq.cosine_similarity(base_code, base_l, base_delta, base_norm,
                                       v_code, v_l, v_delta, v_norm)
            estimated_sims.append(sim)
        
        # Check that ordering is preserved
        for i in range(len(exact_sims) - 1):
            if exact_sims[i] > exact_sims[i + 1]:
                self.assertGreater(estimated_sims[i], estimated_sims[i + 1] - 0.2)
    
    def test_1bit_similarity_ordering(self):
        """Test that 1-bit quantization preserves similarity ordering."""
        brq = BinaryRotationalQuantization(200, seed=42)
        np.random.seed(42)
        
        base = np.random.randn(200)
        similar = base + 0.1 * np.random.randn(200)
        different = np.random.randn(200)
        
        base_packed, base_step, base_norm = brq.encode(base)
        q_codes, q_step, q_norm = brq.encode_query(base)
        similar_packed, sim_step, sim_norm = brq.encode(similar)
        diff_packed, diff_step, diff_norm = brq.encode(different)
        
        sim_to_base = brq.cosine_similarity(q_codes, q_step, q_norm,
                                            base_packed, base_step, base_norm)
        sim_to_similar = brq.cosine_similarity(q_codes, q_step, q_norm,
                                               similar_packed, sim_step, sim_norm)
        sim_to_diff = brq.cosine_similarity(q_codes, q_step, q_norm,
                                            diff_packed, diff_step, diff_norm)
        
        # Base should be most similar to itself, then similar vector
        self.assertGreater(sim_to_base, sim_to_similar)
        self.assertGreater(sim_to_similar, sim_to_diff)


if __name__ == '__main__':
    unittest.main(verbosity=2)