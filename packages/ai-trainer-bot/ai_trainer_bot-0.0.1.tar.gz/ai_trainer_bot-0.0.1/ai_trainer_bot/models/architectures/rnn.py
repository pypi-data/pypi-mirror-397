"""
RNN architectures for AI Trainer Bot.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Optional
from ..base import ClassificationModel
from ..registry import register_model


@register_model('lstm_classifier')
class LSTMClassifier(ClassificationModel):
    """
    LSTM-based classifier.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.vocab_size = config.get('vocab_size', 30000)
        self.embedding_dim = config.get('embedding_dim', 300)
        self.hidden_dim = config.get('hidden_dim', 256)
        self.num_layers = config.get('num_layers', 2)
        self.bidirectional = config.get('bidirectional', True)
        self.dropout_rate = config.get('dropout', 0.5)

        self.embedding = nn.Embedding(self.vocab_size, self.embedding_dim)
        self.lstm = nn.LSTM(
            input_size=self.embedding_dim,
            hidden_size=self.hidden_dim,
            num_layers=self.num_layers,
            bidirectional=self.bidirectional,
            dropout=self.dropout_rate if self.num_layers > 1 else 0,
            batch_first=True
        )

        lstm_output_dim = self.hidden_dim * 2 if self.bidirectional else self.hidden_dim
        self.dropout = nn.Dropout(self.dropout_rate)
        self.classifier = nn.Linear(lstm_output_dim, self.num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embedding_dim)

        lstm_out, (hidden, cell) = self.lstm(embedded)
        # lstm_out: (batch_size, seq_len, hidden_dim * num_directions)

        # Use the last hidden state
        if self.bidirectional:
            hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        else:
            hidden = hidden[-1]

        hidden = self.dropout(hidden)
        output = self.classifier(hidden)
        return output


@register_model('gru_classifier')
class GRUClassifier(ClassificationModel):
    """
    GRU-based classifier.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.vocab_size = config.get('vocab_size', 30000)
        self.embedding_dim = config.get('embedding_dim', 300)
        self.hidden_dim = config.get('hidden_dim', 256)
        self.num_layers = config.get('num_layers', 2)
        self.bidirectional = config.get('bidirectional', True)
        self.dropout_rate = config.get('dropout', 0.5)

        self.embedding = nn.Embedding(self.vocab_size, self.embedding_dim)
        self.gru = nn.GRU(
            input_size=self.embedding_dim,
            hidden_size=self.hidden_dim,
            num_layers=self.num_layers,
            bidirectional=self.bidirectional,
            dropout=self.dropout_rate if self.num_layers > 1 else 0,
            batch_first=True
        )

        gru_output_dim = self.hidden_dim * 2 if self.bidirectional else self.hidden_dim
        self.dropout = nn.Dropout(self.dropout_rate)
        self.classifier = nn.Linear(gru_output_dim, self.num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)

        gru_out, hidden = self.gru(embedded)

        if self.bidirectional:
            hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        else:
            hidden = hidden[-1]

        hidden = self.dropout(hidden)
        output = self.classifier(hidden)
        return output


@register_model('rnn_sequence')
class RNNSequenceModel(nn.Module):
    """
    RNN for sequence modeling tasks.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__()

        self.input_dim = config.get('input_dim', 10)
        self.hidden_dim = config.get('hidden_dim', 128)
        self.num_layers = config.get('num_layers', 2)
        self.output_dim = config.get('output_dim', 1)
        self.rnn_type = config.get('rnn_type', 'LSTM')

        if self.rnn_type == 'LSTM':
            self.rnn = nn.LSTM(self.input_dim, self.hidden_dim, self.num_layers,
                             batch_first=True)
        elif self.rnn_type == 'GRU':
            self.rnn = nn.GRU(self.input_dim, self.hidden_dim, self.num_layers,
                            batch_first=True)
        else:
            self.rnn = nn.RNN(self.input_dim, self.hidden_dim, self.num_layers,
                            batch_first=True)

        self.fc = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_dim)
        rnn_out, _ = self.rnn(x)
        # Take the last output
        last_output = rnn_out[:, -1, :]
        output = self.fc(last_output)
        return output