"""
SCLM Chatbot Example
====================

A simple chatbot with persistent memory across conversation turns.

Run with:
    python examples/chatbot.py
"""

from sclm import SCLMModel


def main():
    print("=" * 60)
    print("🤖 SCLM Chatbot with Memory")
    print("=" * 60)
    print("\nCommands:")
    print("  /reset  - Reset memory")
    print("  /state  - Show memory state")
    print("  /quit   - Exit")
    print("-" * 60)
    
    # Load model
    print("\n⏳ Loading model (this may take a moment)...")
    model = SCLMModel.from_pretrained(
        "mistralai/Mistral-7B-v0.1",
        load_in_4bit=True
    )
    print("✅ Model loaded!\n")
    
    # Initialize conversation
    model.reset_state()
    conversation_history = []
    
    # System context
    system_context = (
        "You are a helpful AI assistant with persistent memory. "
        "You remember what the user tells you throughout the conversation."
    )
    model.add_context(system_context)
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == '/quit':
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == '/reset':
                model.reset_state()
                model.add_context(system_context)
                conversation_history = []
                print("🔄 Memory reset!")
                continue
            elif user_input.lower() == '/state':
                print(f"📊 Memory state norm: {model.state_norm:.4f}")
                print(f"   Conversation turns: {len(conversation_history)}")
                continue
            
            # Add user message to history
            conversation_history.append(f"User: {user_input}")
            
            # Build prompt with recent history
            recent_history = conversation_history[-6:]  # Last 3 exchanges
            prompt = "\n".join(recent_history) + "\nAssistant:"
            
            # Generate response
            full_response = model.generate(
                prompt,
                max_new_tokens=150,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract assistant response
            if "Assistant:" in full_response:
                response = full_response.split("Assistant:")[-1].strip()
            else:
                response = full_response[len(prompt):].strip()
            
            # Clean up response (stop at next speaker)
            if "User:" in response:
                response = response.split("User:")[0].strip()
            
            # Add to history
            conversation_history.append(f"Assistant: {response}")
            
            # Display
            print(f"\n🤖 Assistant: {response}")
            print(f"   [memory: {model.state_norm:.2f}]")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
