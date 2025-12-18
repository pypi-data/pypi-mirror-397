"""
SCLM Document Q&A Example
=========================

Use SCLM as a RAG-like system where context persists in memory
instead of being re-inserted in every prompt.

Run with:
    python examples/document_qa.py
"""

from sclm import SCLMModel
from sclm.utils import MemoryTracker


# Sample document (replace with your own)
SAMPLE_DOCUMENT = """
# Ame Web Studio Company Overview

## About Us
Ame Web Studio is an AI/ML research and development company founded by Mike Amega.
The company is based in Windsor, Ontario, Canada.

## Products

### PixelPro
PixelPro is an AI-powered SaaS platform for content creators. It provides
advanced image processing capabilities using machine learning models.
Website: pixelpro.pro

### SmartMoneyBot
SmartMoneyBot is a sophisticated algorithmic trading system that combines
CNN, LSTM, Transformer, and reinforcement learning approaches for
market prediction and automated trading.

### Color Flow Infinity
Color Flow Infinity is a mobile puzzle game published on Google Play Store.
It has achieved over 1,000 downloads with excellent user engagement.

## Technology Stack
The company specializes in:
- Deep Learning (PyTorch, TensorFlow)
- Natural Language Processing
- Computer Vision
- Quantitative Trading Systems
- Full-Stack Web Development

## Research Focus
Current research includes:
- SCLM: Stateful Coherent Language Models
- EARCP: Novel ensemble architecture
- NEUROGENESIS: Autonomous neural network growth

## Contact
GitHub: https://github.com/Volgat
"""


def chunk_document(text: str, chunk_size: int = 500) -> list:
    """Split document into chunks."""
    paragraphs = text.strip().split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def main():
    print("=" * 70)
    print("📄 SCLM Document Q&A")
    print("=" * 70)
    
    # Load model
    print("\n⏳ Loading model...")
    model = SCLMModel.from_pretrained(
        "mistralai/Mistral-7B-v0.1",
        load_in_4bit=True
    )
    print("✅ Model loaded!")
    
    # Initialize tracker
    tracker = MemoryTracker(model)
    
    # Load document into memory
    print("\n📚 Loading document into memory...")
    chunks = chunk_document(SAMPLE_DOCUMENT)
    
    for i, chunk in enumerate(chunks):
        metrics = tracker.add(chunk)
        print(f"   Chunk {i+1}/{len(chunks)}: state={model.state_norm:.2f}")
    
    print(f"\n✅ Document loaded! Final state norm: {model.state_norm:.2f}")
    
    # Q&A Loop
    print("\n" + "=" * 70)
    print("💬 Ask questions about the document")
    print("   (Type /quit to exit, /reset to clear memory)")
    print("=" * 70)
    
    questions_examples = [
        "What products does Ame Web Studio offer?",
        "Who founded the company?",
        "What is PixelPro?",
        "What research is the company doing?",
        "Where is the company based?",
    ]
    
    print("\nExample questions:")
    for q in questions_examples:
        print(f"   - {q}")
    
    while True:
        try:
            question = input("\n❓ Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() == '/quit':
                print("\n👋 Goodbye!")
                break
            
            if question.lower() == '/reset':
                tracker.reset()
                for chunk in chunks:
                    tracker.add(chunk)
                print(f"🔄 Memory reset! State: {model.state_norm:.2f}")
                continue
            
            # Generate answer
            prompt = f"Based on the document, answer this question: {question}\n\nAnswer:"
            answer = model.generate(prompt, max_new_tokens=150, temperature=0.3)
            
            # Extract answer
            if "Answer:" in answer:
                answer = answer.split("Answer:")[-1].strip()
            else:
                answer = answer[len(prompt):].strip()
            
            print(f"\n📝 Answer: {answer}")
            print(f"   [memory state: {model.state_norm:.2f}]")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
