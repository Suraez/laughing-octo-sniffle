import json
import torch
torch.set_num_threads(1)

from transformers import BertTokenizer, BertModel

# Load once at module import so warm invocations reuse the model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased').eval()

def handler(event, context=None):

    try:
        body = event.get("body", "")
        if isinstance(body, bytes):
            text = body.decode("utf-8")
        elif isinstance(body, str):
            text = body
        else:
            # Some gateways wrap body as a JSON object; accept "text" as fallback
            text = body.get("text", "") if isinstance(body, dict) else str(body)

        encoded_input = tokenizer(text + " [MASK]", return_tensors='pt')

        with torch.no_grad():
            output = model(**encoded_input)

        shape_str = str(tuple(output.last_hidden_state.shape))
        return {
            "statusCode": 200,
            "message": shape_str
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "output_tensor": str(e) 
        }

if __name__ == "__main__":
    # Simple local test
    sample_event = {"body": "hello world"}
    resp = handler(sample_event, None)
