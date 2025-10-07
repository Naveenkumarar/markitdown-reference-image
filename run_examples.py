#!/usr/bin/env python3
"""
Example runner script for markitdown-reference-image package.

This script helps users run the example code easily.
"""

import sys
import os
from pathlib import Path


def list_available_examples():
    """List all available examples."""
    examples_dir = Path(__file__).parent / "markitdown_reference_image" / "examples"
    
    if not examples_dir.exists():
        print("❌ Examples directory not found!")
        return []
    
    examples = []
    for file in examples_dir.glob("*.py"):
        if file.name != "__init__.py":
            examples.append(file.name)
    
    return sorted(examples)


def run_example(example_name):
    """Run a specific example."""
    examples_dir = Path(__file__).parent / "markitdown_reference_image" / "examples"
    example_file = examples_dir / example_name
    
    if not example_file.exists():
        print(f"❌ Example '{example_name}' not found!")
        return False
    
    print(f"🚀 Running example: {example_name}")
    print("=" * 60)
    
    try:
        # Change to the examples directory for relative file paths
        original_cwd = os.getcwd()
        os.chdir(examples_dir)
        
        # Run the example
        exec(open(example_file).read())
        
        print("\n✅ Example completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def main():
    """Main function."""
    print("📚 Markitdown Reference Image - Example Runner")
    print("=" * 60)
    
    examples = list_available_examples()
    
    if not examples:
        print("❌ No examples found!")
        return
    
    print(f"Available examples ({len(examples)}):")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    print("\nOptions:")
    print("  - Run specific example: python run_examples.py <example_name>")
    print("  - Run all examples: python run_examples.py all")
    print("  - Interactive mode: python run_examples.py")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            print("\n🚀 Running all examples...")
            success_count = 0
            for example in examples:
                print(f"\n{'='*60}")
                if run_example(example):
                    success_count += 1
                print(f"{'='*60}")
            
            print(f"\n📊 Results: {success_count}/{len(examples)} examples completed successfully")
            
        elif sys.argv[1] in examples:
            run_example(sys.argv[1])
        else:
            print(f"❌ Unknown example: {sys.argv[1]}")
            print(f"Available examples: {', '.join(examples)}")
    else:
        # Interactive mode
        print("\nEnter example name to run (or 'all' for all examples, 'quit' to exit):")
        while True:
            try:
                choice = input("\n> ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif choice == "all":
                    print("\n🚀 Running all examples...")
                    success_count = 0
                    for example in examples:
                        print(f"\n{'='*60}")
                        if run_example(example):
                            success_count += 1
                        print(f"{'='*60}")
                    
                    print(f"\n📊 Results: {success_count}/{len(examples)} examples completed successfully")
                elif choice in examples:
                    run_example(choice)
                elif choice.isdigit() and 1 <= int(choice) <= len(examples):
                    example_name = examples[int(choice) - 1]
                    run_example(example_name)
                else:
                    print(f"❌ Invalid choice. Available options:")
                    print(f"  - Example names: {', '.join(examples)}")
                    print(f"  - Numbers: 1-{len(examples)}")
                    print(f"  - 'all' to run all examples")
                    print(f"  - 'quit' to exit")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    main()
