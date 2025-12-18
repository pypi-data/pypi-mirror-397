"""
SCLM Basic Usage Example
========================

This example demonstrates the basic usage of SCLM for adding
persistent memory to language models.

Run with:
    python examples/basic_usage.py
"""

from sclm import SCLMModel

def main():
    print("=" * 60)
    print("🧠 SCLM Basic Usage Example")
    print("=" * 60)
    
    # Load model (use 4-bit quantization for less VRAM)
    print("\n📦 Loading model...")
    model = SCLMModel.from_pretrained(
        "mistralai/Mistral-7B-v0.1",
        load_in_4bit=True
    )
    print(f"✅ Model loaded!")
    print(f"   {model}")
    
    # Example 1: Basic generation with memory
    print("\n" + "=" * 60)
    print("📖 Example 1: Memory Persistence")
    print("=" * 60)
    
    model.reset_state()
    print(f"Initial state norm: {model.state_norm:.4f}")
    
    # Add context
    contexts = [
        "The wizard Elara lives in Silverwood forest.",
        "Her familiar is a silver cat named Nimbus.",
        "She discovered an artifact called the Dragon's Eye."
    ]
    
    print("\n📝 Adding context:")
    for ctx in contexts:
        metrics = model.add_context(ctx)
        print(f"   + '{ctx[:40]}...'")
        print(f"     [state: {model.state_norm:.2f}, change: {metrics['state_change']:.4f}]")
    
    # Generate with memory
    prompt = "One day, Elara decided to"
    print(f"\n✨ Generating from: '{prompt}'")
    
    output = model.generate(prompt, max_new_tokens=50)
    generated = output[len(prompt):].strip()
    
    print(f"🤖 Generated: '{generated}'")
    print(f"   [final state: {model.state_norm:.2f}]")
    
    # Check entity retention
    entities = ['elara', 'nimbus', 'silverwood', 'dragon']
    found = [e for e in entities if e in output.lower()]
    print(f"\n📊 Entity Retention: {found} ({len(found)}/{len(entities)})")
    
    # Example 2: Edit Mode
    print("\n" + "=" * 60)
    print("✏️  Example 2: Edit Mode")
    print("=" * 60)
    
    model.reset_state()
    
    # Establish context
    model.add_context("The knight's sword was BLUE and ancient.")
    state_before = model.state_norm
    print(f"State after context: {state_before:.4f}")
    
    # Edit without changing memory
    model.freeze_state()
    print("🔒 State frozen")
    
    output = model.generate("The sword was RED", max_new_tokens=20)
    state_after = model.state_norm
    
    print(f"State after edit: {state_after:.4f}")
    print(f"State changed: {abs(state_after - state_before) > 0.001}")
    
    model.unfreeze_state()
    print("🔓 State unfrozen")
    
    # Example 3: Conversation
    print("\n" + "=" * 60)
    print("💬 Example 3: Multi-turn Conversation")
    print("=" * 60)
    
    model.reset_state()
    
    conversation = [
        "User: My name is Alice and I'm learning Python.",
        "Assistant: Nice to meet you, Alice! Python is a great language to learn.",
        "User: What should I learn first?",
        "Assistant: Start with variables, loops, and functions. They're fundamental.",
        "User: Thanks! Can you remind me of my name?"
    ]
    
    for turn in conversation[:-1]:
        model.add_context(turn)
        print(f"   {turn[:50]}...")
    
    # Generate response
    prompt = conversation[-1] + "\nAssistant:"
    response = model.generate(prompt, max_new_tokens=30)
    generated = response.split("Assistant:")[-1].strip()
    
    print(f"\n🤖 Response: '{generated}'")
    print(f"   (Should remember 'Alice')")
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
