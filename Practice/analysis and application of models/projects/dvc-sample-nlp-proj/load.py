#!/usr/bin/env python3
from transformers import AutoTokenizer, AutoModelForSequenceClassification


if __name__ == '__main__':
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")    

    #model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
    #tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

    tokenizer.save_pretrained('model/tokenizer/')
    model.save_pretrained('model/model/')
