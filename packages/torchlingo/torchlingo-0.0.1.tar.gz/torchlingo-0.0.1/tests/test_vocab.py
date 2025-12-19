import unittest

import torch

from torchlingo import config
from torchlingo.config import Config
from torchlingo.data_processing.vocab import BaseVocab, SimpleVocab


class BaseVocabContractTests(unittest.TestCase):
    """Contract checks for the abstract base vocabulary and alias."""

    def test_base_is_abstract(self):
        """BaseVocab cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseVocab()

    def test_simple_vocab_is_subclass(self):
        """SimpleVocab must subclass BaseVocab for polymorphic use."""
        self.assertTrue(issubclass(SimpleVocab, BaseVocab))


class SimpleVocabInitTests(unittest.TestCase):
    """Initialization behavior for SimpleVocab defaults and overrides."""

    def test_uses_config_defaults(self):
        """Defaults come from global config when no args are provided."""
        vocab = SimpleVocab()
        self.assertEqual(vocab.pad_token, config.PAD_TOKEN)
        self.assertEqual(vocab.unk_token, config.UNK_TOKEN)
        self.assertEqual(vocab.sos_token, config.SOS_TOKEN)
        self.assertEqual(vocab.eos_token, config.EOS_TOKEN)
        self.assertEqual(vocab.pad_idx, config.PAD_IDX)
        self.assertEqual(vocab.unk_idx, config.UNK_IDX)
        self.assertEqual(vocab.sos_idx, config.SOS_IDX)
        self.assertEqual(vocab.eos_idx, config.EOS_IDX)
        self.assertEqual(vocab.min_freq, config.MIN_FREQ)
        self.assertEqual(len(vocab), 4)

    def test_explicit_overrides(self):
        """Explicit kwargs override both defaults and config."""
        vocab = SimpleVocab(
            min_freq=5,
            pad_token="[P]",
            unk_token="[U]",
            sos_token="<S>",
            eos_token="</S>",
            pad_idx=10,
            unk_idx=11,
            sos_idx=12,
            eos_idx=13,
        )
        self.assertEqual(vocab.min_freq, 5)
        self.assertEqual(vocab.pad_token, "[P]")
        self.assertEqual(vocab.unk_idx, 11)

    def test_config_object_overrides_defaults(self):
        """Provided Config object can override default tokens/indices."""
        cfg = Config(min_freq=7, pad_token="<PADDING>", pad_idx=9)
        vocab = SimpleVocab(config=cfg)
        self.assertEqual(vocab.min_freq, 7)
        self.assertEqual(vocab.pad_token, "<PADDING>")
        self.assertEqual(vocab.pad_idx, 9)


class SimpleVocabBuildTests(unittest.TestCase):
    """Vocabulary construction edge cases and frequency handling."""

    def test_counts_tokens_and_respects_min_freq(self):
        """Tokens below min_freq are excluded; counts are tracked."""
        sentences = [
            "hello world from the torch playground today",
            "hello pytorch from the bright sunny lab",
            "hello there from the quiet reading room",
        ]
        vocab = SimpleVocab(min_freq=2)
        vocab.build_vocab(sentences)

        self.assertIn("hello", vocab.token2idx)
        self.assertNotIn("world", vocab.token2idx)
        self.assertEqual(vocab.token_freqs["hello"], 3)

    def test_len_includes_special_tokens(self):
        """Length grows after build but starts with special tokens."""
        vocab = SimpleVocab(min_freq=1)
        initial_len = len(vocab)
        vocab.build_vocab(
            [
                "alpha beta gamma delta epsilon",
                "alpha beta gamma delta zeta",
            ]
        )
        self.assertGreater(len(vocab), initial_len)

    def test_build_is_noop_on_empty(self):
        """Empty input leaves only the four special tokens present."""
        vocab = SimpleVocab(min_freq=1)
        vocab.build_vocab([])
        self.assertEqual(len(vocab), 4)


class SimpleVocabConversionTests(unittest.TestCase):
    """Token/index conversion helpers including unknown handling."""

    def setUp(self) -> None:
        self.vocab = SimpleVocab(min_freq=1)
        self.sentence1 = "hello world from the torch playground today"
        self.sentence2 = "good morning from the bright python universe"
        self.vocab.build_vocab([self.sentence1, self.sentence2])

    def test_token_and_index_roundtrip(self):
        """Tokens map to indices and back without loss."""
        idx = self.vocab.token_to_idx("hello")
        self.assertEqual(self.vocab.idx_to_token(idx), "hello")

    def test_unknown_token_and_index(self):
        """Unknown tokens/indices fall back to UNK defaults."""
        self.assertEqual(self.vocab.token_to_idx("<missing>"), config.UNK_IDX)
        self.assertEqual(self.vocab.idx_to_token(999), config.UNK_TOKEN)

    def test_tokens_to_indices_and_back(self):
        """Batch conversions preserve known tokens and replace unknowns."""
        tokens = ["hello", "world", "<missing>"]
        ids = self.vocab.tokens_to_indices(tokens)
        self.assertEqual(ids[2], config.UNK_IDX)
        roundtrip = self.vocab.indices_to_tokens(ids)
        self.assertEqual(roundtrip[0], "hello")
        self.assertEqual(roundtrip[2], config.UNK_TOKEN)


class SimpleVocabEncodeDecodeTests(unittest.TestCase):
    """End-to-end encode/decode flows for sentences and batches."""

    def setUp(self) -> None:
        self.vocab = SimpleVocab(min_freq=1)
        self.sentence1 = "hello world from the torch playground today"
        self.sentence2 = "good morning from the bright python universe"
        self.vocab.build_vocab([self.sentence1, self.sentence2])

    def test_encode_appends_special_tokens(self):
        """encode adds SOS/EOS when requested."""
        encoded = self.vocab.encode(self.sentence1)
        self.assertEqual(encoded[0], config.SOS_IDX)
        self.assertEqual(encoded[-1], config.EOS_IDX)
        self.assertEqual(len(encoded), len(self.sentence1.split()) + 2)

    def test_encode_without_special_tokens(self):
        """encode can omit special tokens when flagged."""
        encoded = self.vocab.encode(self.sentence1, add_special_tokens=False)
        self.assertEqual(len(encoded), len(self.sentence1.split()))
        self.assertNotIn(config.SOS_IDX, encoded)

    def test_decode_skips_special_tokens(self):
        """decode drops special tokens by default."""
        encoded = [config.SOS_IDX, self.vocab.token_to_idx("hello"), config.EOS_IDX]
        decoded = self.vocab.decode(encoded)
        self.assertEqual(decoded, "hello")

    def test_decode_keeps_special_tokens_when_requested(self):
        """decode can retain special markers when desired."""
        encoded = [config.SOS_IDX, self.vocab.token_to_idx("hello"), config.EOS_IDX]
        decoded = self.vocab.decode(encoded, skip_special_tokens=False)
        self.assertIn(config.SOS_TOKEN, decoded)
        self.assertIn(config.EOS_TOKEN, decoded)

    def test_decode_batch_from_list(self):
        """List-of-lists decode returns list of strings."""
        seq1 = self.vocab.encode(self.sentence1, add_special_tokens=False)
        seq2 = self.vocab.encode(self.sentence2, add_special_tokens=False)
        decoded = self.vocab.decode([seq1, seq2])
        self.assertEqual(decoded, [self.sentence1, self.sentence2])

    def test_decode_batch_from_tensor(self):
        """Tensor batch decode mirrors list batch behavior."""
        seq1 = self.vocab.encode(self.sentence1)
        seq2 = self.vocab.encode(self.sentence2)

        max_len = max(len(seq1), len(seq2))
        pad = self.vocab.pad_idx
        padded = [
            seq1 + [pad] * (max_len - len(seq1)),
            seq2 + [pad] * (max_len - len(seq2)),
        ]

        batch = torch.tensor(padded, dtype=torch.long)
        decoded = self.vocab.decode(batch)

        self.assertEqual(decoded, [self.sentence1, self.sentence2])

    def test_roundtrip_with_empty_sentence(self):
        """Empty string roundtrips to only SOS/EOS and back to blank text."""
        encoded = self.vocab.encode("", add_special_tokens=True)
        self.assertEqual(encoded, [config.SOS_IDX, config.EOS_IDX])
        decoded = self.vocab.decode(encoded)
        self.assertEqual(decoded, "")


if __name__ == "__main__":
    unittest.main()
