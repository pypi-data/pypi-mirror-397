"""
SCLM Interactive Fiction Example
================================

Demonstrates using SCLM for interactive fiction where
characters, locations, and plot elements persist in memory.

Run with:
    python examples/interactive_fiction.py
"""

from sclm import SCLMModel
from sclm.utils import MemoryTracker


def create_story_world(model: SCLMModel) -> None:
    """Establish the story world in memory."""
    world_elements = [
        # Characters
        "Princess Aria is the heir to the throne of Luminara.",
        "Sir Marcus is a loyal knight who has served the royal family for 20 years.",
        "The sorcerer Malachar seeks the Starlight Crown for dark purposes.",
        
        # Locations
        "Castle Luminara sits atop Crystal Mountain, its towers reaching into clouds.",
        "The Whispering Woods surround the castle, said to be enchanted.",
        "The village of Brookhaven lies in the valley below the castle.",
        
        # Plot elements
        "The Starlight Crown is hidden somewhere in the Whispering Woods.",
        "A great feast is planned for Princess Aria's 21st birthday.",
        "Strange creatures have been seen near the forest's edge.",
    ]
    
    print("\n🌍 Building Story World...")
    for element in world_elements:
        model.add_context(element)
        print(f"   + {element[:50]}...")
    
    print(f"   World established! [state: {model.state_norm:.2f}]")


def generate_scene(model: SCLMModel, scene_prompt: str) -> str:
    """Generate a scene continuation."""
    output = model.generate(scene_prompt, max_new_tokens=100, temperature=0.8)
    return output[len(scene_prompt):].strip()


def main():
    print("=" * 70)
    print("📚 SCLM Interactive Fiction Demo")
    print("   'The Crown of Luminara'")
    print("=" * 70)
    
    # Load model
    print("\n🔮 Loading story engine...")
    model = SCLMModel.from_pretrained(
        "mistralai/Mistral-7B-v0.1",
        load_in_4bit=True
    )
    
    # Create story world
    model.reset_state()
    create_story_world(model)
    
    # Track memory through story
    tracker = MemoryTracker(model)
    
    # Chapter 1
    print("\n" + "=" * 70)
    print("📖 Chapter 1: The Morning of the Feast")
    print("=" * 70)
    
    scene1 = "Princess Aria stood on the castle balcony, looking out at"
    print(f"\n✨ {scene1}")
    
    continuation = generate_scene(model, scene1)
    print(f"   {continuation}")
    
    # Update memory with scene
    tracker.add(f"{scene1} {continuation}")
    
    # Chapter 2
    print("\n" + "=" * 70)
    print("📖 Chapter 2: A Warning")
    print("=" * 70)
    
    scene2 = "Sir Marcus rushed into the throne room. 'Your Majesty,' he said urgently,"
    print(f"\n✨ {scene2}")
    
    continuation = generate_scene(model, scene2)
    print(f"   {continuation}")
    
    tracker.add(f"{scene2} {continuation}")
    
    # Chapter 3
    print("\n" + "=" * 70)
    print("📖 Chapter 3: Into the Woods")
    print("=" * 70)
    
    scene3 = "Aria made her decision. She would venture into the Whispering Woods to"
    print(f"\n✨ {scene3}")
    
    continuation = generate_scene(model, scene3)
    print(f"   {continuation}")
    
    tracker.add(f"{scene3} {continuation}")
    
    # Memory Summary
    print("\n" + "=" * 70)
    print("📊 Story Memory Summary")
    print("=" * 70)
    
    summary = tracker.summary()
    print(f"\n   Chapters: {summary['n_turns']}")
    print(f"   State Evolution: {[f'{n:.1f}' for n in summary['state_evolution']]}")
    print(f"   Memory Growth: +{summary['state_growth']:.2f}")
    
    # Check character consistency
    all_text = " ".join(summary['contexts']).lower()
    characters = ['aria', 'marcus', 'malachar', 'luminara']
    found = [c for c in characters if c in all_text]
    print(f"\n   Characters Maintained: {found}")
    
    print("\n" + "=" * 70)
    print("✅ Interactive Fiction Demo Complete!")
    print("=" * 70)
    print("\nNote: SCLM maintains story coherence by keeping")
    print("characters and plot elements in persistent memory.")


if __name__ == "__main__":
    main()
