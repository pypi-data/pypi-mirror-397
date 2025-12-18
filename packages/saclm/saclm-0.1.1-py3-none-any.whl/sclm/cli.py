"""
SCLM Command Line Interface
===========================

Usage:
------
    sclm chat --model mistralai/Mistral-7B-v0.1
    sclm benchmark --model path/to/model
    sclm info --model path/to/model
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='sclm',
        description='SCLM: Stateful Coherent Language Model'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat with SCLM')
    chat_parser.add_argument('--model', '-m', required=True, help='Model name or path')
    chat_parser.add_argument('--4bit', dest='load_4bit', action='store_true', help='Load in 4-bit')
    chat_parser.add_argument('--max-tokens', type=int, default=100, help='Max tokens per response')
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Benchmark SCLM memory')
    bench_parser.add_argument('--model', '-m', required=True, help='Model name or path')
    bench_parser.add_argument('--runs', type=int, default=3, help='Number of benchmark runs')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show model info')
    info_parser.add_argument('--model', '-m', required=True, help='Model name or path')
    
    args = parser.parse_args()
    
    if args.command == 'chat':
        run_chat(args)
    elif args.command == 'benchmark':
        run_benchmark(args)
    elif args.command == 'info':
        run_info(args)
    else:
        parser.print_help()


def run_chat(args):
    """Run interactive chat."""
    print("🧠 SCLM Interactive Chat")
    print("=" * 50)
    print(f"Loading {args.model}...")
    
    from .model import SCLMModel
    
    model = SCLMModel.from_pretrained(
        args.model,
        load_in_4bit=args.load_4bit
    )
    
    print("✅ Model loaded!")
    print("\nCommands:")
    print("  /reset - Reset memory")
    print("  /state - Show state info")
    print("  /quit  - Exit")
    print("-" * 50)
    
    model.reset_state()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == '/quit':
                print("Goodbye!")
                break
            elif user_input.lower() == '/reset':
                model.reset_state()
                print("🔄 Memory reset")
                continue
            elif user_input.lower() == '/state':
                print(f"📊 State norm: {model.state_norm:.4f}")
                continue
            
            # Generate response
            response = model.generate(user_input, max_new_tokens=args.max_tokens)
            generated = response[len(user_input):].strip()
            
            print(f"\n🤖 SCLM: {generated}")
            print(f"   [state: {model.state_norm:.2f}]")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def run_benchmark(args):
    """Run memory benchmark."""
    print("🔬 SCLM Memory Benchmark")
    print("=" * 50)
    
    from .model import SCLMModel
    from .utils import benchmark_memory
    
    print(f"Loading {args.model}...")
    model = SCLMModel.from_pretrained(args.model, load_in_4bit=True)
    
    print("Running benchmark...")
    results = benchmark_memory(
        model,
        contexts=[
            "The wizard Elara lives in Silverwood forest.",
            "Her familiar is a silver cat named Nimbus.",
            "She discovered an ancient artifact called the Dragon's Eye."
        ],
        continuation_prompt="One day, Elara decided to",
        entities=["elara", "nimbus", "silverwood", "dragon"],
        n_runs=args.runs
    )
    
    print("\n📊 Results:")
    print(f"   Entity Retention: {results['entity_retention']:.1%}")
    print(f"   Avg Generation Time: {results['avg_generation_time']:.2f}s")
    print(f"\n   Sample Output:")
    print(f"   {results['sample_output']}")


def run_info(args):
    """Show model information."""
    print("ℹ️  SCLM Model Info")
    print("=" * 50)
    
    from .config import SCLMConfig
    
    path = Path(args.model)
    if path.exists() and (path / "sclm_config.json").exists():
        config = SCLMConfig.load(path / "sclm_config.json")
        params = config.estimate_parameters()
        
        print(f"Base Model: {config.base_model_name}")
        print(f"State Dimension: {config.latent_state_dim}")
        print(f"Injection Layers: {config.state_injection_layers}")
        print(f"Alpha: {config.alpha_inject}")
        print(f"Experts: {config.n_experts}")
        print(f"EARCP Parameters: {params['total_millions']:.1f}M")
    else:
        print(f"Model: {args.model}")
        print("(Load model for detailed info)")


if __name__ == '__main__':
    main()
