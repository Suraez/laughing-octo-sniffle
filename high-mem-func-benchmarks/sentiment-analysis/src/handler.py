import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load a pretrained BERT model for sentiment analysis
model = BertForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model.eval()

# Load the corresponding tokenizer
tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

def handler(event=None, context=None):
    # Hardcoded input text (can be overridden via `event` parameter)
    if event and "text" in event:
        text = event["text"]
    else:
        text = "I absolutely love this product!"  # Example hardcoded text

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Perform inference
    with torch.no_grad():
        outputs = model(**inputs)
        sentiment_scores = outputs.logits
        predicted_class = torch.argmax(sentiment_scores, dim=1).item()

    # Map sentiment scores to labels (0 = Negative, 1 = Neutral, 2 = Positive)
    sentiment_labels = ["very negative", "negative", "neutral", "positive", "very positive"]
    sentiment = sentiment_labels[predicted_class]

    return {"text": text, "sentiment": sentiment}
