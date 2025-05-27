from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json

# Load model and tokenizer at cold start
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
model.eval()

# Fallback prompt
default_prompt = "Once upon a time in a world powered by AI,"

def handle(event, context):
    try:
        # Try parsing JSON from event.body
        try:
            data = json.loads(event.body)
            prompt = data.get("prompt", default_prompt)
        except:
            prompt = default_prompt

        # Tokenize and generate text
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=100, num_return_sequences=1)
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "statusCode": 200,
            "body": json.dumps({"generated_text": text}),
            "headers": { "Content-Type": "application/json" }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": { "Content-Type": "application/json" }
        }
