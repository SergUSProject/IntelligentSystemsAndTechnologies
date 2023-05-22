#!/usr/bin/env python3
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def main():
    classifier = pipeline(
        "sentiment-analysis",
        model=AutoModelForSequenceClassification.from_pretrained('./model/model'),
        tokenizer=AutoTokenizer.from_pretrained("./model/tokenizer"),
    )
    while True:
        inp = input('Enter: ').strip()
        print('Sentiment: ' + str(classifier(inp)))


if __name__ == '__main__':
    main()
