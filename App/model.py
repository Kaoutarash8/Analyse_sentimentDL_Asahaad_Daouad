import torch
import torch.nn.functional as F

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

MODEL_PATH = "darija_bert_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

bert_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

bert_model.eval()


class SentimentModel:

    def __init__(self):

        self.labels = {
            0: "negatif",
            1: "neutre",
            2: "positif"
        }

    def predict(self, text):

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():

            outputs = bert_model(**inputs)

            probs = F.softmax(outputs.logits, dim=1)

            confidence, pred = torch.max(probs, dim=1)

        sentiment = self.labels[pred.item()]

        return sentiment, confidence.item()


model = SentimentModel()