import math
import unittest
import tempfile
from pathlib import Path
from unittest import mock

import torch

from torchlingo.training import train_model, TrainResult
from torchlingo.inference import greedy_decode, beam_search_decode, translate_batch
from torchlingo.config import get_default_config


class DummyTransformer(torch.nn.Module):
    """Minimal Transformer-like model with encode/decode hooks for tests."""

    def __init__(self, vocab_size: int = 10, eos_idx: int = 3):
        super().__init__()
        self.vocab_size = vocab_size
        self.eos_idx = eos_idx
        self.dummy = torch.nn.Parameter(torch.zeros(1))  # ensures device discovery
        self.proj = torch.nn.Linear(4, vocab_size)

    def encode(self, src, src_key_padding_mask=None):
        batch, src_len = src.shape
        return torch.zeros(batch, src_len, 4, device=src.device)

    def decode(
        self,
        tgt,
        memory,
        src_key_padding_mask=None,
        tgt_key_padding_mask=None,
        tgt_mask=None,
    ):
        batch, tgt_len = tgt.shape
        zeros = torch.zeros(batch, tgt_len, 4, device=tgt.device)
        logits = self.proj(zeros)
        logits = logits.clone()
        logits[:, -1, self.eos_idx] += 5.0  # make EOS best
        logits[:, -1, 4] += 4.0  # second-best to test ordering
        return logits

    def forward(self, src, tgt):
        memory = self.encode(src)
        return self.decode(tgt, memory)


class DummyLSTMModel(torch.nn.Module):
    """LSTM-based model exercising the LSTM decode path."""

    def __init__(self, vocab_size: int = 10, eos_idx: int = 3):
        super().__init__()
        self.vocab_size = vocab_size
        self.eos_idx = eos_idx
        self.src_embed = torch.nn.Embedding(vocab_size, 4, padding_idx=0)
        self.tgt_embed = torch.nn.Embedding(vocab_size, 4, padding_idx=0)
        self.encoder = torch.nn.LSTM(4, 4, batch_first=True)
        self.decoder = torch.nn.LSTM(4, 4, batch_first=True)
        self.output = torch.nn.Linear(4, vocab_size)
        torch.nn.init.zeros_(self.output.weight)
        torch.nn.init.zeros_(self.output.bias)
        with torch.no_grad():
            self.output.bias[self.eos_idx] = 5.0

    def forward(self, src, tgt):
        src_emb = self.src_embed(src)
        _, (h, c) = self.encoder(src_emb)
        tgt_emb = self.tgt_embed(tgt)
        dec_out, _ = self.decoder(tgt_emb, (h, c))
        return self.output(dec_out)


class DummyVocab:
    def __init__(self, eos_idx: int = 3, sos_idx: int = 2):
        self.eos_idx = eos_idx
        self.sos_idx = sos_idx

    def encode(self, sentence, add_special_tokens: bool = True):
        tokens = [7]
        if add_special_tokens:
            return [self.sos_idx] + tokens + [self.eos_idx]
        return tokens

    def decode(self, token_ids, skip_special_tokens: bool = True):
        if skip_special_tokens:
            token_ids = [
                t for t in token_ids if t not in (self.sos_idx, self.eos_idx, 0)
            ]
        return "decoded:" + ",".join(str(t) for t in token_ids)


def _toy_loader(batch_size: int = 2):
    src = torch.tensor([[2, 5, 3], [2, 6, 3]], dtype=torch.long)
    tgt = torch.tensor([[2, 8, 3], [2, 9, 3]], dtype=torch.long)
    ds = torch.utils.data.TensorDataset(src, tgt)
    return torch.utils.data.DataLoader(ds, batch_size=batch_size, shuffle=False)


class TrainModelTests(unittest.TestCase):
    def test_train_model_without_validation_returns_losses_and_no_checkpoint(self):
        model = DummyTransformer()
        loader = _toy_loader()
        result = train_model(
            model, train_loader=loader, val_loader=None, num_epochs=2, save_dir=None
        )

        self.assertIsInstance(result, TrainResult)
        self.assertEqual(len(result.train_losses), 2)
        self.assertEqual(result.val_losses, [])
        self.assertIsNone(result.best_checkpoint)

    def test_train_model_with_validation_saves_best_checkpoint(self):
        model = DummyTransformer()
        train_loader = _toy_loader()
        val_loader = _toy_loader()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_model(
                model,
                train_loader=train_loader,
                val_loader=val_loader,
                num_epochs=2,
                save_dir=Path(tmpdir),
                gradient_clip=1.0,
            )

            self.assertEqual(len(result.train_losses), 2)
            self.assertEqual(len(result.val_losses), 2)
            self.assertIsNotNone(result.best_checkpoint)
            self.assertTrue(result.best_checkpoint.exists())

    def test_train_model_honors_gradient_clip(self):
        model = DummyTransformer()
        loader = _toy_loader()
        result = train_model(
            model,
            train_loader=loader,
            val_loader=None,
            num_epochs=1,
            gradient_clip=0.1,
            save_dir=None,
        )
        self.assertEqual(len(result.train_losses), 1)
        self.assertTrue(math.isfinite(result.train_losses[0]))


class GreedyDecodeTests(unittest.TestCase):
    def test_greedy_decode_transformer_path_returns_eos(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        src = torch.tensor([[cfg.sos_idx, 11, cfg.eos_idx]])

        decoded = greedy_decode(model, src, max_len=5, config=cfg)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0][0], cfg.sos_idx)
        self.assertIn(cfg.eos_idx, decoded[0])

    def test_greedy_decode_lstm_path_returns_eos(self):
        cfg = get_default_config()
        model = DummyLSTMModel(eos_idx=cfg.eos_idx)
        src = torch.tensor([[cfg.sos_idx, 8, cfg.eos_idx]])

        decoded = greedy_decode(model, src, max_len=5, config=cfg)
        self.assertEqual(decoded[0][0], cfg.sos_idx)
        self.assertIn(cfg.eos_idx, decoded[0])

    def test_greedy_decode_raises_on_missing_interfaces(self):
        class NoDecode(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.dummy = torch.nn.Parameter(torch.zeros(1))

        model = NoDecode()
        src = torch.tensor([[1, 2, 3]])
        with self.assertRaises(ValueError):
            greedy_decode(model, src)


class BeamSearchDecodeTests(unittest.TestCase):
    def test_beam_search_decode_returns_sequence_with_eos(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        src = torch.tensor([[cfg.sos_idx, 5, cfg.eos_idx]])

        tokens = beam_search_decode(model, src, beam_size=2, max_len=5, config=cfg)
        self.assertEqual(tokens[0], cfg.sos_idx)
        self.assertIn(cfg.eos_idx, tokens)

    def test_beam_search_decode_raises_on_batch_size_gt_one(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        src = torch.tensor(
            [
                [cfg.sos_idx, 5, cfg.eos_idx],
                [cfg.sos_idx, 6, cfg.eos_idx],
            ]
        )
        with self.assertRaises(ValueError):
            beam_search_decode(model, src, beam_size=2, max_len=5, config=cfg)

    def test_beam_search_decode_prefers_higher_log_prob_paths(self):
        cfg = get_default_config()

        class SkewedTransformer(DummyTransformer):
            def decode(
                self,
                tgt,
                memory,
                src_key_padding_mask=None,
                tgt_key_padding_mask=None,
                tgt_mask=None,
            ):
                batch, tgt_len = tgt.shape
                logits = torch.full(
                    (batch, tgt_len, self.vocab_size), -10.0, device=tgt.device
                )
                logits[:, -1, 4] = 6.0
                logits[:, -1, self.eos_idx] = 5.0
                return logits

        model = SkewedTransformer(eos_idx=cfg.eos_idx)
        src = torch.tensor([[cfg.sos_idx, 5, cfg.eos_idx]])
        tokens = beam_search_decode(model, src, beam_size=2, max_len=4, config=cfg)
        self.assertIn(4, tokens)


class TranslateBatchTests(unittest.TestCase):
    def test_translate_batch_greedy_uses_vocab_decode(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        vocab = DummyVocab(eos_idx=cfg.eos_idx, sos_idx=cfg.sos_idx)
        sentences = ["hello", "world"]

        outputs = translate_batch(
            model,
            sentences=sentences,
            src_vocab=vocab,
            tgt_vocab=vocab,
            decode_strategy="greedy",
            max_len=10,
            config=cfg,
        )
        self.assertEqual(len(outputs), len(sentences))
        self.assertTrue(all(o.startswith("decoded:") for o in outputs))

    def test_translate_batch_beam_calls_beam_search(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        vocab = DummyVocab(eos_idx=cfg.eos_idx, sos_idx=cfg.sos_idx)
        sentences = ["only-one"]

        with mock.patch("torchlingo.inference.beam_search_decode") as mock_beam:
            mock_beam.return_value = [cfg.sos_idx, 9, cfg.eos_idx]
            outputs = translate_batch(
                model,
                sentences=sentences,
                src_vocab=vocab,
                tgt_vocab=vocab,
                decode_strategy="beam",
                beam_size=3,
                max_len=10,
                config=cfg,
            )

        mock_beam.assert_called_once()
        self.assertEqual(outputs, ["decoded:9"])

    def test_translate_batch_padding_does_not_break_decoding(self):
        cfg = get_default_config()
        model = DummyTransformer(eos_idx=cfg.eos_idx)
        vocab = DummyVocab(eos_idx=cfg.eos_idx, sos_idx=cfg.sos_idx)
        sentences = ["short", "a much longer sentence to pad"]

        outputs = translate_batch(
            model,
            sentences=sentences,
            src_vocab=vocab,
            tgt_vocab=vocab,
            decode_strategy="greedy",
            max_len=10,
            config=cfg,
        )

        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(o.startswith("decoded:") for o in outputs))


if __name__ == "__main__":
    unittest.main()
