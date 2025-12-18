"""
Transformer architectures for AI Trainer Bot.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Dict, Any, Optional
from ..base import ClassificationModel
from ..registry import register_model


class PositionalEncoding(nn.Module):
    """
    Positional encoding for transformer.
    """

    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                           (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)

        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1)]


@register_model('transformer_classifier')
class TransformerClassifier(ClassificationModel):
    """
    Transformer-based classifier.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.vocab_size = config.get('vocab_size', 30000)
        self.d_model = config.get('d_model', 512)
        self.nhead = config.get('nhead', 8)
        self.num_layers = config.get('num_layers', 6)
        self.dim_feedforward = config.get('dim_feedforward', 2048)
        self.max_len = config.get('max_len', 512)

        self.embedding = nn.Embedding(self.vocab_size, self.d_model)
        self.pos_encoder = PositionalEncoding(self.d_model, self.max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.nhead,
            dim_feedforward=self.dim_feedforward,
            dropout=0.1,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=self.num_layers
        )

        self.classifier = nn.Linear(self.d_model, self.num_classes)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len)
        x = self.embedding(x)  # (batch_size, seq_len, d_model)
        x = self.pos_encoder(x)
        # TransformerEncoder with batch_first=True expects (batch, seq, d_model)
        x = self.transformer_encoder(x)
        x = x.mean(dim=1)  # Global average pooling over sequence dimension
        x = self.dropout(x)
        x = self.classifier(x)
        return x


@register_model('vision_transformer')
class VisionTransformer(ClassificationModel):
    """
    Vision Transformer (ViT) architecture.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.image_size = config.get('image_size', 224)
        self.patch_size = config.get('patch_size', 16)
        self.num_patches = (self.image_size // self.patch_size) ** 2
        self.d_model = config.get('d_model', 768)
        self.nhead = config.get('nhead', 12)
        self.num_layers = config.get('num_layers', 12)
        self.dim_feedforward = config.get('dim_feedforward', 3072)

        self.patch_embed = nn.Conv2d(3, self.d_model,
                                   kernel_size=self.patch_size,
                                   stride=self.patch_size)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, self.d_model))
        self.cls_token = nn.Parameter(torch.zeros(1, 1, self.d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.nhead,
            dim_feedforward=self.dim_feedforward,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, self.num_layers)

        self.classifier = nn.Linear(self.d_model, self.num_classes)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, 3, H, W)
        x = self.patch_embed(x)  # (batch_size, d_model, H//patch_size, W//patch_size)
        x = x.flatten(2).transpose(1, 2)  # (batch_size, num_patches, d_model)

        cls_tokens = self.cls_token.expand(x.shape[0], -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = x + self.pos_embed

        # TransformerEncoder with batch_first=True expects (batch, seq, d_model)
        x = self.transformer(x)
        x = x[:, 0, :]  # Take CLS token (first token in sequence dimension)
        x = self.dropout(x)
        x = self.classifier(x)
        return x