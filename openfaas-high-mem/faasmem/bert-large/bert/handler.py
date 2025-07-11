import torch
torch.set_num_threads(1)

from transformers import BertTokenizer, BertModel

# Load a larger model to increase memory usage
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
model = BertModel.from_pretrained('bert-large-uncased').eval()

def handle(event, context):
    try:
        text = event.body.decode("utf-8")
        encoded_input = tokenizer(text + ' [MASK]', return_tensors='pt')
        with torch.no_grad():
            output = model(**encoded_input)
        return {
            "statusCode": 200,
            "body": str(output.last_hidden_state.shape)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
